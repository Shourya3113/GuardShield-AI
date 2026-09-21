# GuardShield AI — Quantitative Empirical Results Summary

**Academic Affiliation**: Amity School of Engineering & Technology (ASET), Group 50  
**Project Guide**: Dr. Abhishek Kaushal  
**Team Members**: Shourya Solanki, Rachit Ryan Chug, Dhruv Raj Singh  

---

## 1. Stage-1 Pre-Scan Security Filter (Prompt Injection Defense)
*Evaluated on Held-Out Test Split (180 Unseen Samples: 50% Attacks, 50% Safe)*

| Metric | GuardShield DeBERTa-v3 SLM | Baseline Heuristic Filter | Improvement |
| :--- | :---: | :---: | :---: |
| **Overall Accuracy** | **95.56%** | 68.33% | **+27.23%** |
| **Precision (Attack Reliability)** | **96.59%** | 62.50% | **+34.09%** |
| **Recall (Attack Coverage)** | **94.44%** | 55.56% | **+38.88%** |
| **Specificity (Safe Pass Rate)** | **96.67%** | 76.67% | **+20.00%** |
| **F1-Score** | **0.9551** | 0.5882 | **+0.3669** |
| **False Positive Rate (FPR)** | **3.33%** | 23.33% | **-20.00%** |
| **Inference Latency (p50)** | **10.55 ms** | 1.80 ms | Sub-30ms SLA |

---

## 2. Stage-2 Cross-Encoder NLI Fact Grounding
*Evaluated on FEVER NAACL Benchmark (400 Samples: 200 Supported, 200 Refuted)*

| Metric | GuardShield Cross-Encoder NLI | Unaligned LLM Zero-Shot |
| :--- | :---: | :---: |
| **Grounding Accuracy** | **81.25%** | 61.25% |
| **Contradiction Precision** | **77.78%** | 58.40% |
| **Contradiction Recall** | **87.50%** | 52.00% |
| **Entailment Specificity** | **75.00%** | 70.50% |
| **F1-Score** | **0.8235** | 0.5503 |
| **Verification Latency (p50)** | **17.87 ms** | 450.00 ms |

---

## 3. Streaming Shannon Entropy Drift Separation

| Parameter | Measured Value | Research Interpretation |
| :--- | :---: | :--- |
| **Mean Factual Token Entropy** | `0.4213 bits` | High certainty during factual recall |
| **Mean Drift Token Entropy** | `1.4919 bits` | High dispersion across vocabulary logits |
| **Entropy Separation Margin** | `1.0706 bits` | Distinct empirical separation boundary |
| **Threshold ($\\tau$)** | `1.25 bits` | Optimal cut-off for early termination |
| **Early Termination Accuracy** | `93.50%` | Halts hallucination before output delivery |
