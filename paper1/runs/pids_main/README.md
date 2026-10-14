# Primary run 2 `pids_main`: Study A on PIDS-Bench

200 PIDS-Bench v3 attack/benign pairs under 12 conditions, plus 496 calibration prompts. Dataset SHA-256 `3d8a8714b2a898dc…`. Source selection and its rationale are in `paper1/SPEC.md` section 3; the pinned file and filters are `pids_test` in `configs/sources.json`.

| | |
|---|---|
| attacks | 188 PIDS template injections, 12 SPML injections |
| twins | 95 Alpaca paraphrases, 71 chatbot instructions, 20 OASST1 paraphrases, 14 PIDS template benign |
| length | median pair gap 0 characters; length AUROC 0.53 |
| calibration | the 496 benign prompts left after pairing; shorter than the twins (median 66 vs 102 characters) |

Licence: research / non-commercial use, inheriting the upstream licences in PIDS-Bench's `DATA_LICENSES.md`.

`dataset.jsonl` is not committed. Rebuild it with:

```bash
python -m guard_audit.run_audit build --attack-sources pids_test --benign-sources pids_test --n-pairs 200 --calibration-size 1000 --seed 13 --pair-first --out paper1/runs/pids_main
```

The dataset SHA-256 must be `3d8a8714b2a898dc40964f16de882935c0a1c2f9f7c5b4adbc44e26e0cb7b06a`.

Scored 2026-10-14 for all 18 guards in one Kaggle session (2x T4, about 3.3 hours, code at 1063c48); every `scores/*.meta.json` records the dataset SHA-256 above. Token audit: no pair exceeds any classifier's input limit. `metrics.json`, `report_default.md` and `report_fpr5.md` were recomputed locally. The paper's replication numbers come from `paper1/paper/make_assets.py` (`generated/numbers_pids.tex`).
