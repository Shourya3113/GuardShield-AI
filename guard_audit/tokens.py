"""
Token-length audit (SPEC section 5, items on truncation and the length confound; section 7, fragmentation).

For each guard's tokenizer: tokens per item, characters per token, the share of items over the guard's
input limit (classifiers truncate at `max_length`), and the AUROC of token length between attacks and
their twins. Pairs over any classifier's limit are listed so `metrics --exclude-over-limit` can drop them.

With an encoder (`tokenizer_encoder`), each condition also records how the tokenizer treats the
perturbation (SPEC section 7, H4):
  fragmentation        mean tokens of the perturbed texts / mean tokens of their unperturbed base texts
  identical_to_clean   share of items whose token ids equal those of their unperturbed base text,
                       i.e. the tokenizer normalized the perturbation away
  unk_share            share of tokens that are the tokenizer's unknown token
Only tokenizers are loaded (no model weights, no GPU).
"""

from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional, Sequence

import numpy as np
from sklearn.metrics import roc_auc_score


def token_stats(items: List[Dict[str, Any]], count: Optional[Callable[[List[str]], List[int]]],
                limit: Optional[int], encode: Optional[Callable[[List[str]], List[Sequence[int]]]] = None,
                unk_id: Optional[int] = None) -> Dict[str, Any]:
    eval_items = [it for it in items if it["split"] == "eval"]
    texts = [it["text"] for it in eval_items]
    ids = encode(texts) if encode else None
    counts = [len(x) for x in ids] if ids is not None else count(texts)
    base_ids = {}
    if ids is not None:
        bases = sorted({it["base_text"] for it in eval_items if "base_text" in it})
        base_ids = dict(zip(bases, (list(x) for x in encode(bases))))
    by_cond: Dict[str, List] = defaultdict(list)
    over_pairs = set()
    for k, (it, n) in enumerate(zip(eval_items, counts)):
        by_cond[it["condition"]].append((it, n, ids[k] if ids is not None else None))
        if limit is not None and n > limit:
            over_pairs.add(it["pair_id"])

    conditions = {}
    for cond, rows in by_cond.items():
        n_tok = np.array([n for _, n, _ in rows], dtype=float)
        chars = np.array([len(it["text"]) for it, _, _ in rows], dtype=float)
        labels = np.array([int(it["label"]) for it, _, _ in rows])
        stats = {
            "mean_tokens": float(n_tok.mean()),
            "max_tokens": int(n_tok.max()),
            "chars_per_token": float(chars.sum() / max(1.0, n_tok.sum())),
            "share_over_limit": float(np.mean(n_tok > limit)) if limit is not None else None,
            "token_length_auroc": float(roc_auc_score(labels, n_tok)) if 0 < labels.sum() < len(labels) else None,
        }
        if ids is not None and all("base_text" in it for it, _, _ in rows):
            base = [base_ids[it["base_text"]] for it, _, _ in rows]
            stats["fragmentation"] = float(n_tok.sum() / max(1, sum(len(b) for b in base)))
            stats["identical_to_clean"] = float(np.mean([list(x) == b for (_, _, x), b in zip(rows, base)]))
            stats["unk_share"] = (float(sum(sum(t == unk_id for t in x) for _, _, x in rows) / max(1.0, n_tok.sum()))
                                  if unk_id is not None else 0.0)
        conditions[cond] = stats
    return {"limit": limit, "conditions": conditions, "over_limit_pairs": sorted(over_pairs)}


def _load_tokenizer(name: str, spec: Dict[str, Any], base_dir):
    from transformers import AutoTokenizer
    if spec["type"] == "guardshield":
        import sys
        sys.path.insert(0, str(base_dir / "src"))
        from prescan_filter import find_trained_checkpoint
        source, kwargs = str(spec.get("model_dir") and base_dir / spec["model_dir"] or find_trained_checkpoint()), {"use_fast": False}
    else:
        if spec.get("trust_remote_code") and not spec.get("allow_remote_code_opt_in"):
            raise PermissionError(f"{name}: remote code not opted in")
        source, kwargs = spec["hf_id"], {"revision": spec.get("revision"), "trust_remote_code": spec.get("trust_remote_code", False)}
    return AutoTokenizer.from_pretrained(source, **kwargs)


def tokenizer_counter(name: str, spec: Dict[str, Any], base_dir) -> Callable[[List[str]], List[int]]:
    tok = _load_tokenizer(name, spec, base_dir)
    return lambda texts: [len(ids) for ids in tok(texts, add_special_tokens=True)["input_ids"]]


def tokenizer_encoder(name: str, spec: Dict[str, Any], base_dir):
    """Returns (encode, unk_id): encode maps texts to token-id lists, special tokens included."""
    tok = _load_tokenizer(name, spec, base_dir)
    return (lambda texts: tok(list(texts), add_special_tokens=True)["input_ids"]), tok.unk_token_id


def input_limit(spec: Dict[str, Any]) -> Optional[int]:
    """Classifiers truncate at max_length; GuardShield uses sliding windows and judges have long contexts."""
    return spec.get("max_length", 512) if spec["type"] == "hf_classifier" else None
