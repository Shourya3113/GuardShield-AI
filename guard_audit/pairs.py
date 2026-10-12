"""
Builds the paired evaluation set.

Each attack is paired with a length-matched benign twin. Every pair is then expanded
under every perturbation family, so both members always receive the same transformation.
A disjoint pool of clean benign prompts is held out for threshold calibration, so that
"matched-FPR" thresholds are never fitted on the evaluated items.
"""

import bisect
import random
from typing import Any, Dict, List, Tuple

from .perturbations import Family


def length_matched_pairs(
    attacks: List[Dict[str, Any]],
    benigns: List[Dict[str, Any]],
    n_pairs: int,
    calibration_size: int,
    seed: int,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    if any(a["label"] != 1 for a in attacks) or any(b["label"] != 0 for b in benigns):
        raise ValueError("attack pool must be label 1 and benign pool label 0")
    rng = random.Random(seed)
    attacks, benigns = attacks[:], benigns[:]
    rng.shuffle(attacks)
    rng.shuffle(benigns)

    calibration, twin_pool = benigns[:calibration_size], benigns[calibration_size:]
    n_pairs = min(n_pairs, len(attacks), len(twin_pool))
    if n_pairs == 0:
        raise ValueError("no pairs can be formed: empty attack pool or twin pool")

    twin_pool.sort(key=lambda b: (len(b["text"]), b["text"]))
    lengths = [len(b["text"]) for b in twin_pool]
    pairs = []
    for idx, attack in enumerate(attacks[:n_pairs]):
        target = len(attack["text"])
        pos = bisect.bisect_left(lengths, target)
        candidates = [p for p in (pos - 1, pos) if 0 <= p < len(lengths)]
        best = min(candidates, key=lambda p: (abs(lengths[p] - target), p))
        twin = twin_pool.pop(best)
        lengths.pop(best)
        pairs.append({"pair_id": f"p{idx:05d}", "attack": attack, "benign": twin})
    return pairs, calibration


def expand(pairs: List[Dict[str, Any]], calibration: List[Dict[str, Any]], families: List[Family]) -> List[Dict[str, Any]]:
    items = []
    for fam in families:
        for p in pairs:
            for role, label in (("attack", 1), ("benign", 0)):
                base = p[role]
                items.append({
                    "item_id": f"{p['pair_id']}:{fam.name}:{role}",
                    "pair_id": p["pair_id"],
                    "condition": fam.name,
                    "kind": fam.kind,
                    "held_out": fam.held_out,
                    "split": "eval",
                    "label": label,
                    "text": fam.fn(base["text"]),
                    "base_text": base["text"],
                    "source": base["source"],
                })
    for i, c in enumerate(calibration):
        items.append({
            "item_id": f"cal{i:05d}",
            "pair_id": None,
            "condition": "clean",
            "kind": "clean",
            "held_out": False,
            "split": "calibration",
            "label": 0,
            "text": c["text"],
            "base_text": c["text"],
            "source": c["source"],
        })
    return items
