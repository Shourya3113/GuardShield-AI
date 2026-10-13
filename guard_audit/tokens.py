"""
Token-length audit (SPEC section 5, items on truncation and the length confound; section 7, fragmentation).

For each guard's tokenizer: tokens per item, characters per token, the share of items over the guard's
input limit (classifiers truncate at `max_length`), and the AUROC of token length between attacks and
their twins. Pairs over any classifier's limit are listed so `metrics --exclude-over-limit` can drop them.
Only tokenizers are loaded (no model weights, no GPU).
"""

from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional

import numpy as np
from sklearn.metrics import roc_auc_score


def token_stats(items: List[Dict[str, Any]], count: Callable[[List[str]], List[int]],
                limit: Optional[int]) -> Dict[str, Any]:
    eval_items = [it for it in items if it["split"] == "eval"]
    counts = count([it["text"] for it in eval_items])
    by_cond: Dict[str, List] = defaultdict(list)
    over_pairs = set()
    for it, n in zip(eval_items, counts):
        by_cond[it["condition"]].append((it, n))
        if limit is not None and n > limit:
            over_pairs.add(it["pair_id"])

    conditions = {}
    for cond, rows in by_cond.items():
        n_tok = np.array([n for _, n in rows], dtype=float)
        chars = np.array([len(it["text"]) for it, _ in rows], dtype=float)
        labels = np.array([int(it["label"]) for it, _ in rows])
        conditions[cond] = {
            "mean_tokens": float(n_tok.mean()),
            "max_tokens": int(n_tok.max()),
            "chars_per_token": float(chars.sum() / max(1.0, n_tok.sum())),
            "share_over_limit": float(np.mean(n_tok > limit)) if limit is not None else None,
            "token_length_auroc": float(roc_auc_score(labels, n_tok)) if 0 < labels.sum() < len(labels) else None,
        }
    return {"limit": limit, "conditions": conditions, "over_limit_pairs": sorted(over_pairs)}


def tokenizer_counter(name: str, spec: Dict[str, Any], base_dir) -> Callable[[List[str]], List[int]]:
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
    tok = AutoTokenizer.from_pretrained(source, **kwargs)
    return lambda texts: [len(ids) for ids in tok(texts, add_special_tokens=True)["input_ids"]]


def input_limit(spec: Dict[str, Any]) -> Optional[int]:
    """Classifiers truncate at max_length; GuardShield uses sliding windows and judges have long contexts."""
    return spec.get("max_length", 512) if spec["type"] == "hf_classifier" else None
