# Paper 1 draft

`main.tex` is in the IEEE conference template (IEEEtran, numbered citations via natbib + IEEEtranN), as the mentor asked on 2026-10-16; `main_acl.tex` keeps the ACL Rolling Review version. Every result number comes from `generated/`, which `make_assets.py` builds from `paper1/runs/obf_main/metrics.json` and the contamination audit (`contamination.json` of `obf_main` and `pids_main`, `obf_main/metrics_decontaminated.json`). Do not type numbers into the text; add a macro to `make_assets.py` instead (SPEC section 8).

```bash
python paper1/paper/make_assets.py
```

## Building the PDF

There is no LaTeX on the laptop, so build on Overleaf:
1. Upload `overleaf_upload.zip` as a new project (Overleaf already includes IEEEtran.cls and IEEEtranN.bst), or upload `main.tex`, `refs.bib` and the `generated/` folder, keeping the folder name.
2. Compile with pdfLaTeX and BibTeX.

## Word version

The mentor asked for a .docx. `make_docx.py` builds it from `main.tex` (same numbers, citations and cross-references, IEEE two-column layout) and lets Word add the footnote, hyphenation and a check PDF:

```bash
python paper1/paper/make_docx.py
```

Output: `docs/01 Reports/Research Paper/Guards That Reject the Unfamiliar (IEEE).docx`. Rebuild it after every change to `main.tex`; edit `main.tex`, not the .docx.

## Status (2026-10-14)

| Section | State |
|---|---|
| Scope | Paper 1 = Study 1 (audit; SPEC Study A) + Study 2 (mitigation; SPEC Study C) + H4. The Hindi benchmark (SPEC Study B) moved to Paper 2 on 2026-10-14 |
| Abstract, introduction, protocol, metrics, setup | drafted; Study 2 sentences marked `\todo` |
| Study 1 results (Gandalf × Dolly, 18 guards) | drafted from generated numbers |
| Study 1 second source (`pids_main`) | done: replication section and appendix figure |
| Contamination audit | done (`guard_audit/contamination.py`, `configs/training_sources.json`): table and sensitivity analysis generated from both runs' `contamination.json` and `obf_main/metrics_decontaminated.json` |
| Mechanism (H4, tokenizer fragmentation) | done: section "Mechanism: the tokenizer decides" and its table, from `tokens/*.json` (fragmentation, identical_to_clean, unk_share) of both runs |
| Study 2 (canonicalization vs augmentation) | done 2026-10-16: section, Table `tab:study2`, appendix Table `tab:study2-obf`, coupling figure; numbers from `paper1/runs/study_c_*/study_c_summary*.json` and `paper1/study_c/hindi_joiners.json` |
| Related work | drafted; the canonicalization paragraph is `\todo` (Indic related work moves to Paper 2) |
| References | verified 2026-10-14 against the arXiv API, the ACL Anthology and Crossref |
