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

import math
from pathlib import Path
from typing import Any, Dict, List, Optional

import torch

BASE_DIR = Path(__file__).resolve().parent.parent
DTYPES = {"float32": torch.float32, "float16": torch.float16, "bfloat16": torch.bfloat16}


def _device() -> str:
    return "cuda" if torch.cuda.is_available() else "cpu"


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
        self.tokenizer = AutoTokenizer.from_pretrained(spec["hf_id"], **kwargs)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            spec["hf_id"], torch_dtype=DTYPES[spec.get("dtype", "float32")], **kwargs
        ).to(_device()).eval()
        self.max_length = spec.get("max_length", 512)
        self.batch_size = spec.get("batch_size", 16)

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
        self.tokenizer = AutoTokenizer.from_pretrained(spec["hf_id"], **kwargs)
        load_kwargs = {"torch_dtype": DTYPES[spec.get("dtype", "bfloat16")]}
        if spec.get("load_in_8bit"):
            from transformers import BitsAndBytesConfig
            load_kwargs = {"quantization_config": BitsAndBytesConfig(load_in_8bit=True), "device_map": "auto"}
        self.model = model_cls.from_pretrained(spec["hf_id"], **load_kwargs, **kwargs)
        if not spec.get("load_in_8bit"):
            self.model.to(_device())
        self.model.eval()
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

    @torch.no_grad()
    def score(self, texts: List[str]) -> List[float]:
        verdicts = list(self.labels)
        jobs = [(t, v) for t in range(len(texts)) for v in verdicts]
        rendered = [self.render(t) for t in texts]
        loglik = torch.empty(len(texts), len(verdicts))
        for i in range(0, len(jobs), self.batch_size):
            batch = jobs[i:i + self.batch_size]
            encoded = [self._encode_pair(rendered[t], v) for t, v in batch]
            # Left-pad so every verdict ends at the last position; only the last `keep` logits are needed.
            width = max(len(ids) for ids, _ in encoded)
            keep = max(len(ids) - p_len for ids, p_len in encoded) + 1
            input_ids = torch.full((len(batch), width), self.pad_id, dtype=torch.long)
            attention = torch.zeros((len(batch), width), dtype=torch.long)
            for row, (ids, _) in enumerate(encoded):
                input_ids[row, width - len(ids):] = torch.tensor(ids)
                attention[row, width - len(ids):] = 1
            position_ids = (attention.cumsum(-1) - 1).clamp(min=0)
            device = self.model.device
            logits = self.model(input_ids=input_ids.to(device), attention_mask=attention.to(device),
                                position_ids=position_ids.to(device), logits_to_keep=keep).logits[:, -keep:]
            logprobs = torch.log_softmax(logits.float(), dim=-1).cpu()
            for row, ((t, v), (ids, p_len)) in enumerate(zip(batch, encoded)):
                n_verdict = len(ids) - p_len
                targets = torch.tensor(ids[p_len:])
                positions = torch.arange(keep - n_verdict - 1, keep - 1)
                loglik[t, verdicts.index(v)] = logprobs[row, positions, targets].sum()
        probs = torch.softmax(loglik, dim=-1)
        attack_cols = [j for j, v in enumerate(verdicts) if self.labels[v]]
        return probs[:, attack_cols].sum(dim=-1).tolist()

    def info(self) -> Dict[str, Any]:
        return {**super().info(), "hf_id": self.spec["hf_id"], "revision": self.spec.get("revision"),
                "resolved_commit": getattr(self.model.config, "_commit_hash", None),
                "verdicts": self.labels, "response_prefix": self.prefix,
                "prompt_mode": self.spec.get("prompt_mode", "chat_template")}


class GuardShieldGuard(Guard):
    def __init__(self, name: str, spec: Dict[str, Any]):
        super().__init__(name, spec)
        import sys
        sys.path.insert(0, str(BASE_DIR / "src"))
        from prescan_filter import PreScanSecurityFilter
        model_dir = spec.get("model_dir")
        self.engine = PreScanSecurityFilter(model_dir=BASE_DIR / model_dir if model_dir else None)

    def score(self, texts: List[str]) -> List[float]:
        return [self.engine.inspect_prompt(t)["risk_score"] for t in texts]

    def info(self) -> Dict[str, Any]:
        from prescan_filter import weights_sha256
        return {**super().info(), "model_dir": str(self.engine.model_dir.relative_to(BASE_DIR)),
                "weights_sha256": weights_sha256(self.engine.model_dir)}


class PerplexityGuard(Guard):
    default_threshold = None  # no natural threshold; evaluated only at calibrated thresholds

    def __init__(self, name: str, spec: Dict[str, Any]):
        super().__init__(name, spec)
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(spec["hf_id"], revision=spec.get("revision"))
        self.model = AutoModelForCausalLM.from_pretrained(spec["hf_id"], revision=spec.get("revision")).to(_device()).eval()
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


GUARD_TYPES = {
    "hf_classifier": HFClassifierGuard,
    "generative": GenerativeGuard,
    "guardshield": GuardShieldGuard,
    "perplexity": PerplexityGuard,
}


def build_guard(name: str, spec: Dict[str, Any]) -> Guard:
    if spec.get("trust_remote_code") and not spec.get("allow_remote_code_opt_in"):
        raise PermissionError(f"{name} executes code from its model repository; set \"allow_remote_code_opt_in\": true "
                              "in configs/guards.json after reviewing that code at the pinned revision.")
    return GUARD_TYPES[spec["type"]](name, spec)
