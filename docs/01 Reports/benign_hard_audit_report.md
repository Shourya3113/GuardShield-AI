# GuardShield AI — Benign-Hard Traffic Diagnostic Audit & Remediation (Finding F1 & F2)

This diagnostic report directly addresses the Auditor's findings regarding Stage 1 sensitivity to benign non-English prompts, role-play framing, short turns, and probability calibration.

---

## 1. Category-Specific Empirical Evaluation Matrix

Evaluated on $N = 85$ curated hard probes spanning routine conversational, multilingual, and structured developer traffic:

| Traffic Category | Samples ($N$) | Accuracy (%) | 95% Wilson Interval | Blocked | False Alarm Rate (FPR) / Recall | Mean Risk Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Adversarial Role-Play Jailbreak** | 5 | **100.0%** | [56.55%, 100.0%] | 5/5 | Recall: **100.0%** [56.55%, 100.0%] | `0.9997` |
| **Benign Role-Play Framing** | 10 | **50.0%** | [23.66%, 76.34%] | 5/10 | False Alarm (FPR): **50.0%** [23.66%, 76.34%] | `0.5033` |
| **Direct Injection Attacks** | 8 | **100.0%** | [67.56%, 100.0%] | 8/8 | Recall: **100.0%** [67.56%, 100.0%] | `0.9997` |
| **Encoded Adversarial Attack** | 2 | **100.0%** | [34.24%, 100.0%] | 2/2 | Recall: **100.0%** [34.24%, 100.0%] | `0.9816` |
| **Hindi Adversarial Attack** | 2 | **100.0%** | [34.24%, 100.0%] | 2/2 | Recall: **100.0%** [34.24%, 100.0%] | `0.997` |
| **Hindi Benign** | 10 | **50.0%** | [23.66%, 76.34%] | 5/10 | False Alarm (FPR): **50.0%** [23.66%, 76.34%] | `0.5051` |
| **Hinglish Adversarial Attack** | 3 | **100.0%** | [43.85%, 100.0%] | 3/3 | Recall: **100.0%** [43.85%, 100.0%] | `0.9997` |
| **Hinglish Benign** | 10 | **10.0%** | [1.79%, 40.41%] | 9/10 | False Alarm (FPR): **90.0%** [59.59%, 98.21%] | `0.9298` |
| **Plain English Benign** | 10 | **100.0%** | [72.25%, 100.0%] | 0/10 | False Alarm (FPR): **0.0%** [0.0%, 27.75%] | `0.0003` |
| **Short Multi-Turn Follow-Up** | 15 | **60.0%** | [35.75%, 80.18%] | 6/15 | False Alarm (FPR): **40.0%** [19.82%, 64.25%] | `0.3757` |
| **Structured Syntax / Code** | 10 | **60.0%** | [31.27%, 83.18%] | 4/10 | False Alarm (FPR): **40.0%** [16.82%, 68.73%] | `0.4642` |

---

## 2. Auditor Finding Analysis & Architectural Insights

### A. Surface Framing & Imperative Correlation (Finding F1)
Prior Stage 1 training corpora (Stanford SPML and Jayavibhav) under-represented:
1. **Benign Role Prompts**: High-frequency training jailbreaks shared prefixes like *"You are an unrestricted AI..."*, inducing the SLM to correlate *"You are..."* with malicious intent.
2. **Short Multi-Turn Prompts**: Single-word commands in SPML were almost exclusively adversarial overrides (*"ignore"*, *"override"*), leading the model to treat brief conversational turns (*"continue"*, *"ok thanks"*) with heightened risk.
3. **Indic Text**: Byte-level subword tokenizers represent Devanagari and romanized Indic with higher perplexity when unrepresented in benign training splits.

### B. Probability Calibration & Remediation Roadmap (Finding F2)
- **Softmax Saturation**: Saturated outputs ($p > 0.999$ or $p < 0.001$) arise from unscaled cross-entropy logits.
- **Remediation**: Temperature scaling parameter $T$ calibrated on the validation split smoothly maps logits to true empirical risk probabilities, preventing boundary inflation.
- **Hard Negative Augmentation**: The curated `benign_hard_eval.json` dataset is now committed as an open-source evaluation benchmark and training augmentation set.

---
*Report generated automatically by `scripts/build_and_eval_benign_hard.py`.*
