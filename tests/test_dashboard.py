"""Dashboard data plumbing: the shared logprob parser and the results loaders (no models, no Streamlit server)."""

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "dashboard"))

import data  # noqa: E402
from proxy_server import top_probs_from_choice  # noqa: E402


def test_top_probs_from_choice_reads_both_logprob_layouts():
    lps = [{"token": "a", "logprob": math.log(0.5)}, {"token": "b", "logprob": math.log(0.25)}]
    new_style = {"logprobs": {"content": [{"token": "a", "logprob": math.log(0.5), "top_logprobs": lps}]}}
    old_style = {"logprobs": {"top_logprobs": lps}}
    for choice in (new_style, old_style):
        assert [round(p, 6) for p in top_probs_from_choice(choice)] == [0.5, 0.25]


def test_top_probs_from_choice_without_logprobs_is_empty():
    assert top_probs_from_choice({}) == []
    assert top_probs_from_choice({"logprobs": None}) == []
    assert top_probs_from_choice({"logprobs": {"content": []}}) == []


def test_failure_map_matches_metrics_file():
    fm = data.failure_map("obf_main")
    assert len(fm["rows"]) == 19 and len(fm["columns"]) == 12
    raw = json.loads((ROOT / "paper1/runs/obf_main/metrics.json").read_text(encoding="utf-8"))["guards"]
    cell = fm["cells"][fm["rows"].index("ProtectAI v2")][fm["columns"].index("B64")]
    expected = raw["protectai_v2"]["conditions"]["base64_wrap"]
    assert cell["auroc"] == expected["auroc"]
    assert cell["mode"] == expected["policies"]["default"]["failure_mode"]


def test_failure_counts_agree_with_paper_macros():
    m = data.macros()
    n = data.failure_counts(data.failure_map("obf_main"))
    assert n["cells"] == int(m["nCells"])
    assert n["destroyed"] == int(m["nSigDestroyed"])
    assert (n["fail_closed"], n["fail_open"], n["both"]) == (int(m["nModeClosed"]), int(m["nModeOpen"]), int(m["nModeBoth"]))


def test_study2_and_coupling_rows():
    m = data.macros()
    rows = data.study2(m)
    assert [r["arm"] for r in rows][0] == "No fix (retrained)" and len(rows) == 5
    assert [p["ratio"] for p in data.coupling(m)] == [0.0, 0.25, 0.5, 1.0]
