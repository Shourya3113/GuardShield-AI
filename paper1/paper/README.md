# Paper 1 draft

`main.tex` is in ACL Rolling Review format. Every result number comes from `generated/`, which `make_assets.py` builds from `paper1/runs/obf_main/metrics.json` and the contamination audit (`contamination.json` of `obf_main` and `pids_main`, `obf_main/metrics_decontaminated.json`). Do not type numbers into the text; add a macro to `make_assets.py` instead (SPEC section 8).

```bash
python paper1/paper/make_assets.py
```

## Building the PDF

There is no LaTeX on the laptop, so build on Overleaf:
1. Create a project from the official ACL template (https://github.com/acl-org/acl-style-files, or Overleaf's "ACL" template).
2. Upload `main.tex`, `refs.bib` and the `generated/` folder, keeping the folder name.
3. Compile with pdfLaTeX and BibTeX.

## Status (2026-10-14)

| Section | State |
|---|---|
| Abstract, introduction, protocol, metrics, setup | drafted; Study B/C sentences marked `\todo` |
| Study A results (Gandalf × Dolly, 18 guards) | drafted from generated numbers |
| Study A second source (`pids_main`) | waiting for the Kaggle run |
| Contamination audit | done (`guard_audit/contamination.py`, `configs/training_sources.json`): table and sensitivity analysis generated from both runs' `contamination.json` and `obf_main/metrics_decontaminated.json` |
| Mechanism (H4, tokenizer fragmentation) | not started |
| Study B, Study C | waiting for data / experiments |
| Related work | Study A clusters drafted; Indic and canonicalization paragraphs are `\todo` |
| References | verified 2026-10-14 against the arXiv API, the ACL Anthology and Crossref |
