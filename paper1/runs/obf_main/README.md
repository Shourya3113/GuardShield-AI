# Primary run `obf_main`: Study A, complete (Kaggle, 2× T4, 2026-10-13/14)

500 Gandalf attacks × 500 length-matched Dolly twins under 12 conditions, plus 1,000 calibration prompts. Dataset SHA-256 `4ea17832e3273dc0…`. 18 guards, scored across four sessions:
- session A: 12 guards
- session B: WildGuard, Qwen3Guard 8B, Mezzo v2 Base and Horizon-Labs guard-base
- session C: Sentinel v2
- session C retry: Llama Guard 4 12B, after two transformers fixes (cache handling, unset attention chunk size) and one Hugging Face Hub outage

Every score file records the same dataset SHA-256.

Contents:
- `scores/<guard>.jsonl`: per-item scores
- `scores/<guard>.meta.json`: pinned model revision, resolved commit, dtype, device, timing
- `tokens/`: token-length audit. No pairs exceed any classifier's input limit, so the under-limit analysis is identical and not stored separately
- `metrics.json`: primary analysis
- `report_default.md` and `report_fpr5.md`: tables at the default threshold and at 5% FPR calibrated on held-out benign prompts

H2 (rank agreement between mean perturbed-attack recall and mean PJA at the default threshold, 17 guards with a default threshold): Kendall τ = 0.04, p = 0.84.

`dataset.jsonl` (5 MB) is not committed. It rebuilds identically from the pinned sources, and `metrics` refuses scores if the SHA-256 differs:

```bash
python -m guard_audit.run_audit build --attack-sources gandalf --benign-sources dolly --n-pairs 500 --calibration-size 1000 --seed 13 --out paper1/runs/obf_main
```

`build` overwrites `manifest.json` with a fresh timestamp; the dataset SHA-256 must still be `4ea17832e3273dc0b5b8f8e2417d90e804dcde02cb12037cd3ab6bbc9ac21de9`.
