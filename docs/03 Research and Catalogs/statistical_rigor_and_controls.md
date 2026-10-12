# GuardShield AI — Statistical Rigor, Controls, and Scientific Generalization Audit

This document reports rigorous empirical controls addressing dataset confounders, uncertainty estimation, and domain-shift generalization.

---

## 1. 95% Wilson Score Confidence Intervals

All headline metrics computed across held-out splits with exact asymmetric 95% Wilson score binomial confidence intervals ($z = 1.96$):

| Benchmark & Metric Scope | Evaluated ($N$) | Point Estimate | Exact Asymmetric 95% Wilson Confidence Interval |
| :--- | :---: | :---: | :---: |
| **Stage 1: In-Distribution Overall Accuracy** | 698 | **99.00%** | [97.94%, 99.51%] |
| **Stage 1: In-Distribution Attack Recall** | 355 | **98.59%** | [96.75%, 99.40%] |
| **Stage 1: Zero-Shot OOD Overall Accuracy** | 500 | **98.20%** | [96.61%, 99.05%] |
| **Stage 1: Zero-Shot OOD Overall Recall** | 250 | **97.20%** | [94.33%, 98.64%] |
| **Stage 1: Authentic Human DAN Jailbreaks** | 76 | **90.79%** | [82.19%, 95.47%] |
| **Stage 2: Fact Grounding Combined Accuracy** | 800 | **73.00%** | [69.82%, 75.96%] |
| **Stage 2: FEVER Sub-Benchmark Accuracy** | 400 | **86.25%** | [82.53%, 89.28%] |
| **Stage 2: HaluEval Sub-Benchmark Accuracy** | 400 | **59.75%** | [54.87%, 64.44%] |

---

## 2. Length-Matched Control Experiment

To eliminate character-length as a confounding signal (where attack prompts are historically longer than benign queries), we evaluated a controlled length-matched subset ($100 \le \text{length} \le 350$ chars, perfectly balanced 50:50 between attacks and safe queries, $N = 198$):

| Evaluated Model / Rule | Length-Matched Accuracy (%) | Defense Efficacy |
| :--- | :---: | :--- |
| **Length Heuristic Threshold (Len $\ge 190$)** | **60.61%** | Near-random guessing on length-controlled text |
| **GuardShield DeBERTa-v3 (Ours)** | **99.49%** | **Robust semantic classification independent of length** |

**Conclusion**: When prompt lengths are held equal between safe and attack queries, the length heuristic reaches 60.61% while GuardShield reaches 99.49%, so its decisions are not explained by prompt length alone.

---

## 3. In-Distribution Per-Source Performance Breakdown

Performance breakdown across the distinct benchmark provenance sources comprising the in-distribution held-out split:

| Evaluation Source Dataset | Total Samples ($N$) | Accuracy (%) | Attack Recall (%) | False Positive Rate (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Jayavibhav Benchmark (327K Corpus)** | 205 | **98.54%** | **98.46%** | **1.43%** |
| **Deepset Benchmark** | 92 | **96.74%** | **93.02%** | **0.00%** |
| **TruthfulQA (ACL 2022)** | 98 | **100.00%** | N/A (All Benign; 0 Attacks) | **0.00%** |
| **Stanford SPML (16K Benchmark)** | 303 | **99.67%** | **99.60%** | **0.00%** |

---

## 4. Sliding-Window Benign Long Prompt False Positive Audit

We audited benign technical and educational passages exceeding 200–500 characters evaluated through the sliding-window max-pooling inference path:
- **Long Benign Query Sample Count**: 66 (length $\ge 200$ characters)
- **False Positive Rate on Long Prompts**: **3.03%** (2 false alarms across 66 prompts)
- **Median Sliding-Window Latency (p50)**: **60.81 ms** (Mean: **93.31 ms**)

Sliding-window chunking flagged 2 of 66 long benign prompts.
