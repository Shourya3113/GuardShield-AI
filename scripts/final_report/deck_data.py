"""Numbers for the presentation deck (make_deck.js), printed as JSON from the same files as the report and paper."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "dashboard"))
import data  # noqa: E402

m = data.macros()
r1 = data.report("raw_eval_in_distribution_test_698")["metrics"]
r2 = data.report("raw_eval_out_of_distribution_500")["metrics"]
pai, tf = data.report("table_external_baseline_protectai"), data.report("table_tfidf_baseline_comparison")
keys = ["nGuards", "nPairs", "nFamilies", "nCells", "nSigDestroyed", "pctSigDestroyed", "nAttackRobust", "nAttackRobustFC",
        "pctAttackRobustFC", "hTwoTau", "nMixedGuards", "replDirCells", "mechObfNormalized", "mechObfNormalizedIntact",
        "mechObfUnknown", "mechObfUnknownDestroyed", "mechObfFragmented", "mechObfFragmentedDestroyed", "mechObfDirPct",
        "guardshieldShyFPR", "guardshieldCleanFPR", "scPidsNoneSeenWrapperFpr", "scPidsScriptReplaceSeenWrapperFpr"]
print(json.dumps({
    "recall": r1["recall"], "fpr": r1["fpr"], "ood_recall": r2["recall"], "lat": r1["latency_p50_ms"],
    "pipe_lat": data.report("raw_eval_pipeline_e2e")["metrics"]["latency_p50_ms"],
    "base": {"labels": ["TF-IDF + LR", "ProtectAI v2", "GuardShield (ours)"],
             "in": [tf["in_distribution"]["recall"], pai["in_distribution"]["recall"], r1["recall"]],
             "out": [tf["out_of_distribution"]["recall"], pai["out_of_distribution"]["recall"], r2["recall"]]},
    "m": {k: m[k] for k in keys},
    "study2": data.study2(m),
    "failure_map": str(ROOT / "paper1" / "paper" / "generated" / "fig_failure_map.png"),
}))
