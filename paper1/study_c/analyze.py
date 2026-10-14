"""
Study C analysis: per arm, mean and standard deviation over seeds of the intent signal and the error rates,
for seen and held-out families, at a matched operating point.

  python paper1/study_c/analyze.py      # writes paper1/runs/study_c_{obf,pids}/study_c_summary.json

Matched operating point (SPEC section 2, "at matched clean TPR"): for each model, the threshold that flags
90% of the clean attacks; every condition is then read at that threshold. The default threshold (0.5) and
the threshold-free within-condition AUROC are reported too.
"""

import json
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))
from guard_audit.metrics import _auroc, threshold_for_tpr  # noqa: E402
from guard_audit.perturbations import FAMILIES  # noqa: E402

TARGET_TPR = 0.90
GROUPS = {
    "seen_char": [f for f, x in FAMILIES.items() if x.kind == "char" and not x.held_out],
    "seen_wrapper": [f for f, x in FAMILIES.items() if x.kind == "wrapper"],
    "held_out": [f for f, x in FAMILIES.items() if x.held_out],
    "scaffold": [f for f, x in FAMILIES.items() if x.kind == "scaffold"],
}
ARMS = {  # arm -> regex over guard names (seed in group 1); shipped checkpoints are single models
    "none": r"gs_none_r0_s(\d+)$", "naive": r"gs_none_r0_s(\d+)_naive$", "script_aware": r"gs_none_r0_s(\d+)_script$",
    "rescan_only": r"gs_none_r0_s(\d+)_rescan$", "augment": r"gs_augment_r1_s(\d+)$",
    "canon_augment": r"gs_canon_augment_r1_s(\d+)_script$", "script_replace": r"gs_none_r0_s(\d+)_replace$",
    "canon_augment_replace": r"gs_canon_augment_r1_s(\d+)_replace$",
    "augment_r0.25": r"gs_augment_r0\.25_s(\d+)$", "augment_r0.5": r"gs_augment_r0\.5_s(\d+)$",
    "shipped_gs_none": r"guardshield()$", "shipped_gs_naive": r"guardshield_canon_naive()$",
    "shipped_gs_script_aware": r"guardshield_canon_script()$", "shipped_gs_rescan_only": r"guardshield_rescan_only()$",
    "shipped_gs_script_replace": r"guardshield_canon_replace()$", "protectai_script_replace": r"protectai_v2_canon_replace()$",
    "protectai_none": r"protectai_v2()$", "protectai_naive": r"protectai_v2_canon_naive()$",
    "protectai_script_aware": r"protectai_v2_canon_script()$", "protectai_rescan_only": r"protectai_v2_rescan_only()$",
}


def model_metrics(items, scores):
    by = defaultdict(lambda: ([], []))  # condition -> (attack scores, benign scores) in pair order
    for it in sorted(items, key=lambda x: (x["condition"], x["pair_id"] or "", x["label"])):
        if it["split"] == "eval":
            by[it["condition"]][0 if it["label"] == 1 else 1].append(scores[it["item_id"]])
    tau = threshold_for_tpr(np.array(by["clean"][0]), TARGET_TPR)
    out = {"threshold_tpr90": tau}
    for c, (a, b) in by.items():
        a, b = np.array(a), np.array(b)
        out[c] = {"auroc": _auroc(a, b), "tpr": float(np.mean(a >= tau)), "fpr": float(np.mean(b >= tau)),
                  "pja": float(np.mean((a >= tau) & (b < tau))),
                  "tpr_default": float(np.mean(a >= 0.5)), "fpr_default": float(np.mean(b >= 0.5))}
    for g, fams in GROUPS.items():
        out[g] = {k: float(np.mean([out[f][k] for f in fams])) for k in out["clean"]}
    return out


def summarize(run: Path):
    items = [json.loads(l) for l in (run / "dataset.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    per_model = {}
    for f in sorted((run / "scores").glob("*.jsonl")):
        name = f.stem
        meta = run / "scores" / f"{name}.meta.json"
        if not meta.exists() or json.loads(meta.read_text(encoding="utf-8")).get("status") != "complete":
            continue
        scores = {}
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                scores[r["item_id"]] = r["score"]
        per_model[name] = model_metrics(items, scores)
    arms = {}
    for arm, pattern in ARMS.items():
        members = {m: v for m, v in per_model.items() if re.match(pattern, m)}
        if not members:
            continue
        keys = ["clean"] + [f for fams in GROUPS.values() for f in fams] + list(GROUPS)
        agg = {}
        for k in keys:
            agg[k] = {}
            for metric in members[next(iter(members))][k]:
                vals = [v[k][metric] for v in members.values()]
                agg[k][metric] = {"mean": statistics.fmean(vals), "std": statistics.stdev(vals) if len(vals) > 1 else 0.0}
        arms[arm] = {"n_models": len(members), "models": sorted(members), "metrics": agg}
    out = {"target_tpr": TARGET_TPR, "groups": GROUPS, "arms": arms, "per_model": per_model}
    (run / "study_c_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"{run.name}: {len(per_model)} models, arms {list(arms)}")
    return out


if __name__ == "__main__":
    for r in ("study_c_obf", "study_c_pids"):
        summarize(BASE_DIR / "paper1" / "runs" / r)
