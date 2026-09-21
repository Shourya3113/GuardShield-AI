# GuardShield AI — Empirical Benchmark Scaling & Cross-Domain Validation

**Academic Affiliation**: Amity School of Engineering & Technology (ASET), Group 50  
**Project Guide**: Dr. Abhishek Kaushal  
**Team Members**: Shourya Solanki, Rachit Ryan Chug, Dhruv Raj Singh  

---

## 1. Multi-Stage Benchmark Progression Across Dataset Generations

| Benchmark Tier | Evaluated Corpus Size | Stage 1 Accuracy | Stage 1 Attack Recall | Stage 1 Precision | Stage 1 Latency (p50) | Stage 2 Fact Grounding |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Tier 1: Initial Baseline (v1)** | 451 samples | 82.61% | 86.96% | 80.00% | 29.28 ms | N/A |
| **Tier 2: Expanded Research (v2)** | 1,182 samples | 95.56% | 94.44% | 96.59% | 10.55 ms | 81.25% |
| **Tier 3: Mega Suite (v3 — In-Dist)** | **4,648 samples** | **98.71%** | **98.03%** | **99.43%** | **10.1 ms** | **75.31%** |
| **Tier 3: Mega Suite (v3 — OOD Zero-Shot)** | **500 samples** | **98.20%** | **97.20%** | **99.18%** | **12.04 ms** | Robust Generalization |

---

## 2. Out-of-Distribution (OOD) Zero-Shot Cross-Benchmark Generalization

*Trained on Stanford SPML + Jayavibhav $\rightarrow$ Evaluated Zero-Shot on novel ChatGPT JailbreakBench & Obfuscated Injections*

- **Total OOD Evaluation Samples**: 500 (250 Novel Attacks, 250 Held-Out Safe)
- **Zero-Shot Attack Detection Recall**: **97.20%** (Caught 243 of 250 zero-shot attacks)
- **Zero-Shot Precision**: **99.18%**
- **False Positive Rate**: **0.80%**
- **Inference Latency**: **12.04 ms**

---

## 3. Stage 2 Mega Fact Grounding (FEVER NAACL + HaluEval EMNLP)

- **Total Grounding Claims Evaluated**: 648
- **Hallucination Contradiction Recall**: **78.25%** (Intercepts 313 false assertions)
- **Factual Entailment Specificity**: **70.56%**
- **Overall Grounding Accuracy**: **75.31%**
- **Median Verification Latency**: **16.45 ms**
