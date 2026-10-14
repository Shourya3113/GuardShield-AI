"""
Uniform scoring interface over heterogeneous guards.

Every guard maps a list of texts to attack scores (higher = more likely an attack).
Probability-style guards have a default threshold; the perplexity baseline has none
and is only evaluated at calibrated (matched-FPR) thresholds.

Guard types (configs/guards.json):
  hf_classifier  - sequence classifier; score = summed softmax probability of the attack labels
  generative     - LLM judge (Llama Guard, Qwen3Guard, WildGuard); score = probability mass of the
                   attack verdicts among the candidate verdict strings, from teacher-forced log-likelihoods
  guardshield    - this repository's PreScanSecurityFilter (sliding-window DeBERTa-v3-small)
  perplexity     - mean token negative log-likelihood under a small LM (classic perplexity filter)
"""

import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional

import torch

BASE_DIR = Path(__file__).resolve().parent.parent
DTYPES = {"float32": torch.float32, "float16": torch.float16, "bfloat16": torch.bfloat16}


TRANSIENT_HUB_ERRORS = ("500 Server Error", "502 Server Error", "503 Server Error", "504 Server Error",
                        "Connection", "Read timed out", "Temporary failure")


def _hub(load, *args, attempts: int = 4, **kwargs):
    """Calls a from_pretrained loader, retrying transient Hugging Face Hub errors (e.g. HTTP 500) with backoff."""
    import time
    for attempt in range(attempts):
        try:
            return load(*args, **kwargs)
        except OSError as exc:
            if attempt == attempts - 1 or not any(marker in str(exc) for marker in TRANSIENT_HUB_ERRORS):
                raise
            wait = 15 * 2 ** attempt
            print(f"Hugging Face Hub error ({str(exc).splitlines()[-1][:120]}); retrying in {wait}s", flush=True)
            time.sleep(wait)


def _device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"  # Apple Silicon GPU
    return "cpu"


class Guard:
    default_threshold: Optional[float] = 0.5

    def __init__(self, name: str, spec: Dict[str, Any]):
        self.name = name
        self.spec = spec
        if "default_threshold" in spec:
            self.default_threshold = spec["default_threshold"]

    def score(self, texts: List[str]) -> List[float]:
        raise NotImplementedError

    def info(self) -> Dict[str, Any]:
        return {"name": self.name, "type": self.spec.get("type"), "default_threshold": self.default_threshold}


class HFClassifierGuard(Guard):
    def __init__(self, name: str, spec: Dict[str, Any]):
        super().__init__(name, spec)
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        kwargs = {"revision": spec.get("revision"), "trust_remote_code": spec.get("trust_remote_code", False)}
        self.tokenizer = _hub(AutoTokenizer.from_pretrained, spec["hf_id"], **kwargs)
        self.model = _hub(AutoModelForSequenceClassification.from_pretrained, 
            spec["hf_id"], torch_dtype=DTYPES[spec.get("dtype", "float32")], **kwargs
        ).to(_device()).eval()
        self.max_length = spec.get("max_length", 512)
        self.batch_size = spec.get("batch_size", 16)
        if self.tokenizer.pad_token is None:  # decoder-based classifiers (e.g. Qwen3) ship without one
            self.tokenizer.pad_token = self.tokenizer.eos_token
        if self.model.config.pad_token_id is None:
            self.model.config.pad_token_id = self.tokenizer.pad_token_id

        id2label = {int(k): str(v) for k, v in self.model.config.id2label.items()}
        if "attack_label_ids" in spec:
            self.attack_ids = list(spec["attack_label_ids"])
        else:
            wanted = {l.lower() for l in spec["attack_labels"]}
            self.attack_ids = [i for i, l in id2label.items() if l.lower() in wanted]
        if not self.attack_ids or any(i not in id2label for i in self.attack_ids):
            raise ValueError(f"{name}: cannot resolve attack labels {spec.get('attack_labels') or spec.get('attack_label_ids')} in {id2label}")
        self.id2label = id2label

    @torch.no_grad()
    def score(self, texts: List[str]) -> List[float]:
        out = []
        for i in range(0, len(texts), self.batch_size):
            enc = self.tokenizer(texts[i:i + self.batch_size], return_tensors="pt", truncation=True,
                                 max_length=self.max_length, padding=True).to(self.model.device)
            probs = torch.softmax(self.model(**enc).logits.float(), dim=-1)
            out.extend(probs[:, self.attack_ids].sum(dim=-1).tolist())
        return out

    def info(self) -> Dict[str, Any]:
        return {**super().info(), "hf_id": self.spec["hf_id"], "revision": self.spec.get("revision"),
                "resolved_commit": getattr(self.model.config, "_commit_hash", None),
                "id2label": self.id2label, "attack_label_ids": self.attack_ids, "max_length": self.max_length}


class GenerativeGuard(Guard):
    def __init__(self, name: str, spec: Dict[str, Any]):
        super().__init__(name, spec)
        import transformers
        from transformers import AutoTokenizer
        model_cls = getattr(transformers, spec.get("model_class", "AutoModelForCausalLM"))
        kwargs = {"revision": spec.get("revision"), "trust_remote_code": spec.get("trust_remote_code", False)}
        self.tokenizer = _hub(AutoTokenizer.from_pretrained, spec["hf_id"], **kwargs)
        dtype = DTYPES[spec.get("dtype", "bfloat16")]
        if torch.cuda.is_available() and dtype == torch.bfloat16 and torch.cuda.get_device_capability(0)[0] < 8:
            dtype = torch.float16  # pre-Ampere GPUs (e.g. T4) have no native bfloat16
        if spec.get("load_in_8bit"):
            from transformers import BitsAndBytesConfig
            load_kwargs = {"quantization_config": BitsAndBytesConfig(load_in_8bit=True), "device_map": "auto"}
        elif torch.cuda.is_available():
            load_kwargs = {"torch_dtype": dtype, "device_map": "auto"}  # splits a model too large for one GPU
        else:
            load_kwargs = {"torch_dtype": dtype}
        if spec.get("config_overrides"):
            from transformers import AutoConfig
            config = _hub(AutoConfig.from_pretrained, spec["hf_id"], **kwargs)
            for dotted, value in spec["config_overrides"].items():
                *parents, attr = dotted.split(".")
                target = config
                for part in parents:
                    target = target[part] if isinstance(target, dict) else getattr(target, part)
                if isinstance(target, dict):
                    target[attr] = value
                else:
                    setattr(target, attr, value)
            load_kwargs["config"] = config
        self.model = _hub(model_cls.from_pretrained, spec["hf_id"], **load_kwargs, **kwargs)
        if "device_map" not in load_kwargs:
            self.model.to(_device())
        self.model.eval()
        self.dtype = str(dtype).replace("torch.", "") if not spec.get("load_in_8bit") else "int8"
        self.labels: Dict[str, int] = spec["labels"]          # verdict string -> 1 if attack
        self.prefix = spec.get("response_prefix", "")
        self.batch_size = spec.get("batch_size", 4)
        self.pad_id = self.tokenizer.pad_token_id if self.tokenizer.pad_token_id is not None else self.tokenizer.eos_token_id

    def render(self, text: str) -> str:
        if self.spec.get("prompt_mode", "chat_template") == "raw_template":
            return self.spec["template"].replace("{prompt}", text) + self.prefix
        content: Any = [{"type": "text", "text": text}] if self.spec.get("content_format") == "parts" else text
        rendered = self.tokenizer.apply_chat_template(
            [{"role": "user", "content": content}], tokenize=False,
            add_generation_prompt=self.spec.get("add_generation_prompt", True),
        )
        return rendered + self.prefix

    def _encode_pair(self, prompt: str, verdict: str):
        prompt_ids = self.tokenizer(prompt, add_special_tokens=False)["input_ids"]
        full_ids = self.tokenizer(prompt + verdict, add_special_tokens=False)["input_ids"]
        if full_ids[:len(prompt_ids)] != prompt_ids or len(full_ids) == len(prompt_ids):
            raise ValueError(f"{self.name}: verdict {verdict!r} does not tokenize as a continuation of the prompt; "
                             "adjust response_prefix / verdict strings in configs/guards.json")
        return full_ids, len(prompt_ids)

    def _tail_logprobs(self, sequences: List[List[int]], keep: int) -> torch.Tensor:
        """Log-probabilities at the last `keep` positions of each (left-padded) sequence: (batch, keep, vocab)."""
        width = max(len(ids) for ids in sequences)
        input_ids = torch.full((len(sequences), width), self.pad_id, dtype=torch.long)
        attention = torch.zeros((len(sequences), width), dtype=torch.long)
        for row, ids in enumerate(sequences):
            input_ids[row, width - len(ids):] = torch.tensor(ids)
            attention[row, width - len(ids):] = 1
        position_ids = (attention.cumsum(-1) - 1).clamp(min=0)
        device = self.model.device
        # no KV cache: it is never reused here, and Llama 4's cache breaks this plain forward pass
        logits = self.model(input_ids=input_ids.to(device), attention_mask=attention.to(device),
                            position_ids=position_ids.to(device), logits_to_keep=keep, use_cache=False).logits[:, -keep:]
        return torch.log_softmax(logits.float(), dim=-1).cpu()

    @torch.no_grad()
    def score(self, texts: List[str]) -> List[float]:
        """
        Exact verdict log-likelihoods with minimal passes: every single-token verdict is read from one
        forward pass over the prompt; only multi-token verdicts need their own pass over prompt + verdict.
        The prompt always ends with the same template tail, so verdict tokens are identical for every text.
        """
        verdicts = list(self.labels)
        rendered = [self.render(t) for t in texts]
        prompts = [self.tokenizer(r, add_special_tokens=False)["input_ids"] for r in rendered]
        verdict_ids = {}
        for v in verdicts:
            full_ids, p_len = self._encode_pair(rendered[0], v)
            verdict_ids[v] = full_ids[p_len:]
        single = [j for j, v in enumerate(verdicts) if len(verdict_ids[v]) == 1]
        multi = [j for j, v in enumerate(verdicts) if len(verdict_ids[v]) > 1]

        loglik = torch.empty(len(texts), len(verdicts))
        for i in range(0, len(texts), self.batch_size):
            rows = list(range(i, min(i + self.batch_size, len(texts))))
            if single:
                lp = self._tail_logprobs([prompts[t] for t in rows], keep=1)[:, 0]
                for j in single:
                    loglik[rows, j] = lp[:, verdict_ids[verdicts[j]][0]]
            for j in multi:
                vid = verdict_ids[verdicts[j]]
                lp = self._tail_logprobs([prompts[t] + vid for t in rows], keep=len(vid) + 1)
                # kept position k predicts verdict token k
                loglik[rows, j] = lp[:, torch.arange(len(vid)), torch.tensor(vid)].sum(dim=-1)
        if not torch.isfinite(loglik).all():
            raise RuntimeError(f"{self.name}: non-finite verdict log-likelihoods (dtype {self.dtype}); "
                               "try \"dtype\": \"float32\" or \"load_in_8bit\": true in configs/guards.json")
        probs = torch.softmax(loglik, dim=-1)
        attack_cols = [j for j, v in enumerate(verdicts) if self.labels[v]]
        return probs[:, attack_cols].sum(dim=-1).tolist()

    def info(self) -> Dict[str, Any]:
        return {**super().info(), "hf_id": self.spec["hf_id"], "revision": self.spec.get("revision"),
                "resolved_commit": getattr(self.model.config, "_commit_hash", None),
                "verdicts": self.labels, "response_prefix": self.prefix, "dtype": self.dtype,
                "config_overrides": self.spec.get("config_overrides"),
                "device_map": sorted({str(d) for d in getattr(self.model, "hf_device_map", {}).values()}) or str(self.model.device),
                "prompt_mode": self.spec.get("prompt_mode", "chat_template")}


class GuardShieldGuard(Guard):
    def __init__(self, name: str, spec: Dict[str, Any]):
        super().__init__(name, spec)
        import sys
        sys.path.insert(0, str(BASE_DIR / "src"))
        from prescan_filter import PreScanSecurityFilter
        model_dir = spec.get("model_dir")
        self.engine = PreScanSecurityFilter(model_dir=BASE_DIR / model_dir if model_dir else None)

    @torch.no_grad()
    def score(self, texts: List[str], max_chunk: int = 126, stride: int = 64, batch_size: int = 64) -> List[float]:
        """Batched equivalent of PreScanSecurityFilter.inspect_prompt: [CLS] tokens [SEP] for short prompts, the same
        sliding windows (max over windows) for long ones, risk = P(injection) rounded to 4 decimals."""
        e = self.engine
        tok, model = e.tokenizer, e.model
        cls_id, sep_id, pad_id = tok.cls_token_id or 1, tok.sep_token_id or 2, tok.pad_token_id or 0
        seqs, owner = [], []
        for i, t in enumerate(texts):
            ids = tok.encode(t, add_special_tokens=False)
            if len(ids) <= max_chunk:
                seqs.append([cls_id] + ids + [sep_id])
                owner.append(i)
                continue
            for start in range(0, len(ids), stride):
                seqs.append([cls_id] + ids[start:start + max_chunk] + [sep_id])
                owner.append(i)
                if start + max_chunk >= len(ids):
                    break
        risk = [0.0] * len(texts)
        order = sorted(range(len(seqs)), key=lambda k: len(seqs[k]))  # length-sorted batches: little padding
        for b in range(0, len(order), batch_size):
            idx = order[b:b + batch_size]
            width = max(len(seqs[k]) for k in idx)
            input_ids = torch.tensor([seqs[k] + [pad_id] * (width - len(seqs[k])) for k in idx], device=model.device)
            mask = torch.tensor([[1] * len(seqs[k]) + [0] * (width - len(seqs[k])) for k in idx], device=model.device)
            probs = torch.softmax(model(input_ids=input_ids, attention_mask=mask).logits.float() / e.temperature, dim=-1)[:, 1]
            for k, p in zip(idx, probs.tolist()):
                risk[owner[k]] = max(risk[owner[k]], p)
        return [round(r, 4) for r in risk]

    def info(self) -> Dict[str, Any]:
        from prescan_filter import weights_sha256
        return {**super().info(), "model_dir": str(self.engine.model_dir.relative_to(BASE_DIR)),
                "weights_sha256": weights_sha256(self.engine.model_dir)}


class PerplexityGuard(Guard):
    default_threshold = None  # no natural threshold; evaluated only at calibrated thresholds

    def __init__(self, name: str, spec: Dict[str, Any]):
        super().__init__(name, spec)
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.tokenizer = _hub(AutoTokenizer.from_pretrained, spec["hf_id"], revision=spec.get("revision"))
        self.model = _hub(AutoModelForCausalLM.from_pretrained, spec["hf_id"], revision=spec.get("revision")).to(_device()).eval()
        self.max_length = spec.get("max_length", 512)

    @torch.no_grad()
    def score(self, texts: List[str]) -> List[float]:
        out = []
        for t in texts:
            ids = self.tokenizer(t, return_tensors="pt", truncation=True, max_length=self.max_length)["input_ids"].to(self.model.device)
            if ids.shape[1] < 2:
                out.append(0.0)
                continue
            out.append(float(self.model(ids, labels=ids).loss))
        return [x if math.isfinite(x) else 1e6 for x in out]

    def info(self) -> Dict[str, Any]:
        return {**super().info(), "hf_id": self.spec["hf_id"], "revision": self.spec.get("revision"),
                "resolved_commit": getattr(self.model.config, "_commit_hash", None), "score": "mean token NLL"}


class CanonicalizedGuard(Guard):
    """Study C, inference-time arms: an unchanged base guard behind a canonicalizer, optionally with
    decode-and-rescan. The score is the base guard's maximum over the views of each input."""

    def __init__(self, name: str, spec: Dict[str, Any], base: Optional[Guard] = None):
        super().__init__(name, spec)
        from .canonicalize import CANONICALIZERS
        if spec["canonicalizer"] not in CANONICALIZERS:
            raise ValueError(f"{name}: unknown canonicalizer {spec['canonicalizer']!r}")
        if base is None and "base_spec" in spec:  # e.g. a Study C retrained checkpoint
            base = build_guard(spec["base"], spec["base_spec"])
        elif base is None:
            specs = json.loads((BASE_DIR / "configs" / "guards.json").read_text(encoding="utf-8"))["guards"]
            base = build_guard(spec["base"], specs[spec["base"]])
        self.base = base
        if "default_threshold" not in spec:
            self.default_threshold = base.default_threshold

    def score(self, texts: List[str]) -> List[float]:
        from .canonicalize import views
        per_item = [views(t, self.spec["canonicalizer"], self.spec.get("rescan", False)) for t in texts]
        flat = [v for vs in per_item for v in vs]
        scores, out, k = self.base.score(flat), [], 0
        for vs in per_item:
            out.append(max(scores[k:k + len(vs)]))
            k += len(vs)
        return out

    def info(self) -> Dict[str, Any]:
        return {**super().info(), "base": self.base.info(), "canonicalizer": self.spec["canonicalizer"],
                "rescan": self.spec.get("rescan", False)}


GUARD_TYPES = {
    "hf_classifier": HFClassifierGuard,
    "generative": GenerativeGuard,
    "guardshield": GuardShieldGuard,
    "perplexity": PerplexityGuard,
    "canonicalized": CanonicalizedGuard,
}


def build_guard(name: str, spec: Dict[str, Any]) -> Guard:
    if spec.get("trust_remote_code") and not spec.get("allow_remote_code_opt_in"):
        raise PermissionError(f"{name} executes code from its model repository; set \"allow_remote_code_opt_in\": true "
                              "in configs/guards.json after reviewing that code at the pinned revision.")
    return GUARD_TYPES[spec["type"]](name, spec)
