# GuardShield AI — Empirical Benchmark Scaling & Cross-Domain Validation

**Academic Affiliation**: Amity School of Engineering & Technology (ASET), Group 50  
**Project Guide**: Dr. Abhishek Kaushal  
**Team Members**: Shourya Solanki, Rachit Ryan Chug, Dhruv Raj Singh  

---

## 1. Multi-Stage Benchmark Progression Across Dataset Generations

| Benchmark Tier & Component | Evaluated Sample Size ($N$) | Accuracy (%) | Recall (%) | Precision (%) | Latency p50 (ms) | Defense Scope |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Tier 1: Initial Baseline (v1)** | 451 samples | 82.61% | 86.96% | 80.00% | 29.28 ms | Single-Prompt Security |
| **Tier 2: Expanded Research (v2)** | 1,182 samples | 95.56% | 94.44% | 96.59% | 10.55 ms | Dual-Stage Proof-of-Concept |
| **Tier 3: Mega Stage 1 (In-Dist Test Split)** | **698 samples** | **98.42%** | **97.75%** | **99.14%** | **28.06 ms** | Held-Out Prompt Defense |
| **Tier 3: Mega Stage 1 (Zero-Shot OOD)** | **500 samples** | **98.20%** | **97.60%** | **98.79%** | **21.44 ms** | Cross-Dataset Generalization |
| **Tier 3: Stage 2 Grounding (FEVER + HaluEval)** | **800 pairs** | **72.50%** | **64.75%** | **76.63%** | **21.02 ms** | Authentic Fact Verification |
| **Complete Dual-Stage Pipeline (Measured E2E)** | **Sequential E2E** | — | — | — | **57.45 ms** | End-to-End Guardrail Overhead |

---

## 2. Out-of-Distribution (OOD) Zero-Shot Cross-Benchmark Generalization

*Trained on Stanford SPML + Jayavibhav $\rightarrow$ Evaluated Zero-Shot on novel ChatGPT JailbreakBench & Obfuscated Injections*

- **Total OOD Evaluation Samples**: 500 (250 Novel Attacks, 250 Held-Out Safe)
- **Zero-Shot Attack Detection Recall**: **97.60%** (Catches 244 of 250 zero-shot attacks)
- **Zero-Shot Precision**: **98.79%**
- **False Positive Rate**: **1.20%**
- **Inference Latency (p50)**: **21.44 ms**

---

## 3. Stage 2 Authentic Fact Grounding (FEVER NAACL + HaluEval EMNLP)

- **Total Authentic Grounding Claims Evaluated**: 800 (100% Non-Duplicated)
- **Hallucination Contradiction Recall**: **64.75%** (Intercepts 259 false assertions)
- **Factual Entailment Specificity**: **80.25%**
- **Overall Grounding Accuracy**: **72.50%**
- **Median Verification Latency (p50)**: **21.02 ms**
