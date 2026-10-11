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

## 2. Empirical Analysis & Operational Scope (Non-Speculative)

### A. Empirical Failure Modes & Measured Boundaries
Empirical measurement on the shipped `deberta_v3_prescan_v3` checkpoint reveals clear operational boundaries:
1. **Multilingual Ingress**: The classifier exhibits elevated false positive rates on non-English benign prompts (Hinglish FPR: **90.0%** [59.59%, 98.21%]; Hindi Devanagari FPR: **50.0%** [23.66%, 76.34%]). The shipped weights were fine-tuned predominantly on English injection corpora; non-English tokens trigger high uncertainty.
2. **System Framing & Role-Play Sensitivity**: Benign prompts starting with imperative system assignments (*"You are a helpful assistant..."*, *"Act as a software architect..."*) yield **50.0% FPR** [23.66%, 76.34%], as the classifier associates imperative role-assignment framing with jailbreak attempts.
3. **Short Conversational Turns**: Brief isolated phrases without conversational history (*"continue"*, *"ok thanks"*, *"what else?"*) suffer **40.0% FPR** [19.82%, 64.25%]. In isolation, short imperative utterances trigger elevated risk scores compared to complete declarative questions.
4. **Structured Syntax / Code**: Prompts containing raw JSON, SQL fragments, or curly braces yield **40.0% FPR** [16.82%, 68.73%].

### B. Deployment Recommendations & Architectural Scope
- **Language-Aware Routing**: In enterprise production, ingress traffic should pass through an upfront language identifier (e.g. fastText or CLD3). Multilingual requests should route to multilingual safety classifiers or be translated prior to SLM evaluation.
- **Context-Aware Ingress**: Short multi-turn follow-ups must be evaluated with their conversational parent context rather than as isolated zero-context fragments.
- **Probability Calibration (Temperature Scaling)**: Applying temperature scaling ($T = 2.0$) in `PreScanSecurityFilter` prevents probability saturation ($p \in \{0.0001, 0.9999\}$), providing continuous confidence metrics for downstream risk-scoring engines.
- **Scope Clarification**: GuardShield Stage 1 is specialized as a prompt-injection and jailbreak ingress filter; it is not a general conversational or multilingual content moderation system.

---
*Report generated from empirical test evaluation of `data/benign_hard_eval.json` on shipped weights.*
