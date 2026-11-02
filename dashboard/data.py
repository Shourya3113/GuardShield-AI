"""
Read-only access to the committed results for the dashboard's Results tab (no Streamlit here, so it is testable).

Every number shown in the dashboard comes from the same files as the final report and the paper:
docs/01 Reports/*.json (the GuardShield system), paper1/runs/*/metrics.json (Study 1) and the generated
paper macros (paper1/paper/generated/numbers*.tex, Study 2).
"""

import importlib.util
import json
import re
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "docs" / "01 Reports"
RUNS = ROOT / "paper1" / "runs"
GENERATED = ROOT / "paper1" / "paper" / "generated"

SOURCES = {"Gandalf × Dolly (500 pairs)": "obf_main", "PIDS-Bench (200 pairs)": "pids_main"}
MODE_LABEL = {"fail_closed": "fail-closed", "fail_open": "fail-open", "both": "both", "stable": "stable", None: "n/a"}


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def report(name: str) -> Dict[str, Any]:
    """One of the system result files in docs/01 Reports, e.g. 'raw_eval_in_distribution_test_698'."""
    return _load_json(REPORTS / f"{name}.json")


def _paper_layout():
    """Detector and family order and labels, taken from the paper's asset generator so both always agree."""
    spec = importlib.util.spec_from_file_location("make_assets", ROOT / "paper1" / "paper" / "make_assets.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.GUARDS, mod.FAMILIES


def failure_map(run: str) -> Dict[str, Any]:
    """Study 1 cells for one run: rows (detectors) x columns (clean + 11 families) with mode, signal and rates."""
    guards, families = _paper_layout()
    metrics = _load_json(RUNS / run / "metrics.json")["guards"]
    columns = [("clean", "Clean", "clean")] + list(families)
    cells = []
    for g, g_label, kind in guards:
        row = []
        for f, f_label, f_kind in columns:
            c = metrics[g]["conditions"][f]
            pol = c.get("policies", {}).get("default", {})
            row.append({
                "detector": g_label, "family": f_label, "family_kind": f_kind,
                "auroc": c["auroc"], "ci": c.get("auroc_ci95"), "signal": c.get("signal"),
                "mode": None if f == "clean" else pol.get("failure_mode"),
                "tpr": (pol.get("tpr") or {}).get("value"), "fpr": (pol.get("fpr") or {}).get("value"),
            })
        cells.append(row)
    return {"rows": [g_label for _, g_label, _ in guards], "columns": [c[1] for c in columns], "cells": cells}


def failure_counts(fm: Dict[str, Any]) -> Dict[str, int]:
    """Headline counts over the perturbed cells (excludes the clean column)."""
    out = {"intact": 0, "degraded": 0, "destroyed": 0, "fail_closed": 0, "fail_open": 0, "both": 0, "stable": 0, "cells": 0}
    for row in fm["cells"]:
        for c in row[1:]:
            out["cells"] += 1
            if c["signal"] in out:
                out[c["signal"]] += 1
            if c["mode"] in out:
                out[c["mode"]] += 1
    return out


def macros() -> Dict[str, str]:
    """The paper's generated \\newcommand values (Study 2 numbers and headline counts)."""
    out = {}
    for f in GENERATED.glob("numbers*.tex"):
        for line in f.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\\newcommand\{\\([A-Za-z]+)\}\{(.*)\}$", line.strip())
            if m:
                out[m.group(1)] = m.group(2).replace("{,}", ",")
    return out


STUDY2_ARMS = [("None", "No fix (retrained)"), ("Naive", "Naive canonicalizer"), ("ScriptAware", "Script-aware canonicalizer"),
               ("Augment", "Benign-twin augmentation"), ("CanonAugment", "Canonicalize + augment")]


def study2(m: Dict[str, str]) -> List[Dict[str, Any]]:
    """Per-arm seen-character-family AUROC on both sources and benign FPR at 90% recall on PIDS-Bench."""
    return [{"arm": label, "pids_auc": float(m[f"scPids{k}SeenCharAuc"]), "gandalf_auc": float(m[f"scObf{k}SeenCharAuc"]),
             "pids_fpr": float(m[f"scPids{k}SeenCharFpr"])} for k, label in STUDY2_ARMS]


def coupling(m: Dict[str, str]) -> List[Dict[str, float]]:
    """Benign-twin augmentation over training mixtures (PIDS-Bench, default threshold, seen character families)."""
    pts = [(0.0, "None"), (0.25, "AugmentQuarter"), (0.5, "AugmentHalf"), (1.0, "Augment")]
    return [{"ratio": r, "recall": float(m[f"scPids{k}SeenCharTprDefault"]), "fpr": float(m[f"scPids{k}SeenCharFprDefault"])} for r, k in pts]
