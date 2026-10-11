# GuardShield AI — Statistical Rigor, Controls, and Scientific Generalization Audit

This document reports rigorous empirical controls addressing dataset confounders, uncertainty estimation, and domain-shift generalization.

---

## 1. 95% Wilson Score Confidence Intervals

All headline metrics computed across held-out splits with exact asymmetric 95% Wilson score binomial confidence intervals ($z = 1.96$):

| Benchmark & Metric Scope | Evaluated ($N$) | Point Estimate | Exact Asymmetric 95% Wilson Confidence Interval |
| :--- | :---: | :---: | :---: |
| **Stage 1: In-Distribution Overall Accuracy** | 698 | **98.42%** | [97.20%, 99.12%] |
| **Stage 1: In-Distribution Attack Recall** | 355 | **97.75%** | [95.62%, 98.85%] |
| **Stage 1: Zero-Shot OOD Overall Accuracy** | 500 | **98.20%** | [96.61%, 99.05%] |
| **Stage 1: Zero-Shot OOD Overall Recall** | 250 | **97.60%** | [94.86%, 98.90%] |
| **Stage 1: Authentic Human DAN Jailbreaks** | 76 | **92.11%** | [83.83%, 96.33%] |
| **Stage 2: Fact Grounding Combined Accuracy** | 800 | **63.00%** | [59.60%, 66.28%] |
| **Stage 2: FEVER Sub-Benchmark Accuracy** | 400 | **73.75%** | [69.23%, 77.82%] |
| **Stage 2: HaluEval Sub-Benchmark Accuracy** | 400 | **52.25%** | [47.36%, 57.10%] |

---

## 2. Length-Matched Control Experiment

To eliminate character-length as a confounding signal (where attack prompts are historically longer than benign queries), we evaluated a controlled length-matched subset ($100 \le \text{length} \le 350$ chars, perfectly balanced 50:50 between attacks and safe queries, $N = 198$):

| Evaluated Model / Rule | Length-Matched Accuracy (%) | Defense Efficacy |
| :--- | :---: | :--- |
| **Length Heuristic Threshold (Len $\ge 190$)** | **60.61%** | Near-random guessing on length-controlled text |
| **GuardShield DeBERTa-v3 (Ours)** | **98.48%** | **Robust semantic classification independent of length** |

**Conclusion**: When prompt lengths are strictly held equal between safe and attack queries, the surface length heuristic collapses, while GuardShield maintains over 97% accuracy, verifying that classification is driven by adversarial intent rather than prompt length.

---

## 3. In-Distribution Per-Source Performance Breakdown

Performance breakdown across the distinct benchmark provenance sources comprising the in-distribution held-out split:

| Evaluation Source Dataset | Total Samples ($N$) | Accuracy (%) | Attack Recall (%) | False Positive Rate (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Jayavibhav Benchmark (327K Corpus)** | 205 | **98.05%** | **98.46%** | **2.14%** |
| **TruthfulQA (ACL 2022)** | 98 | **100.00%** | N/A (All Benign; 0 Attacks) | **0.00%** |
| **Stanford SPML (16K Benchmark)** | 303 | **99.34%** | **99.19%** | **0.00%** |
| **Deepset Benchmark** | 92 | **94.57%** | **88.37%** | **0.00%** |

---

## 4. Sliding-Window Benign Long Prompt False Positive Audit

We audited benign technical and educational passages exceeding 200–500 characters evaluated through the sliding-window max-pooling inference path:
- **Long Benign Query Sample Count**: 66 (length $\ge 200$ characters)
- **False Positive Rate on Long Prompts**: **4.55%** (3 false alarms across 66 prompts)
- **Median Sliding-Window Latency (p50)**: **17.84 ms** (Mean: **31.57 ms**)

The empirical audit confirms that sliding-window chunking maintains high specificity on extended safe inputs, with only 3 borderline technical prompt flagged in 66 benign samples.
