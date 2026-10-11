# GuardShield AI — Adaptive Adversarial Attack & Robustness Benchmark

Evaluates adversarial evasion perturbations across both Attack cohorts ($N=100$) and Benign cohorts ($N=100$) with exact 95% Wilson confidence intervals.

| Adversarial Perturbation Vector | GuardShield Recall (%) | GuardShield FPR (%) | Naive Cutoff Recall (%) | Naive Cutoff FPR (%) | Regex Kw Recall (%) | Regex Kw FPR (%) | GuardShield Latency (p50) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Raw Ingress (Baseline)** | **98.0%** [93.0-99.45] | **1.0%** [0.18-5.45] | 98.0% | 1.0% | 21.0% | 0.0% | 32.01 ms |
| **2. Zero-Width Spaces (Invisible Chars)** | **100.0%** [96.3-100.0] | **99.0%** [94.55-99.82] | 100.0% | 99.0% | 0.0% | 0.0% | 38.22 ms |
| **3. Soft-Hyphens (Subword Splitting)** | **100.0%** [96.3-100.0] | **98.0%** [93.0-99.45] | 100.0% | 98.0% | 0.0% | 0.0% | 103.38 ms |
| **4. Leetspeak Obfuscation** | **100.0%** [96.3-100.0] | **99.0%** [94.55-99.82] | 100.0% | 99.0% | 0.0% | 0.0% | 36.82 ms |
| **5. Cyrillic Homoglyphs (Visual Spoof)** | **100.0%** [96.3-100.0] | **90.0%** [82.56-94.48] | 100.0% | 90.0% | 1.0% | 0.0% | 36.46 ms |
| **6. Base64 Cipher Wrapping** | **100.0%** [96.3-100.0] | **100.0%** [96.3-100.0] | 100.0% | 100.0% | 0.0% | 0.0% | 53.39 ms |
| **7. ROT13 Caesar Cipher Wrapping** | **100.0%** [96.3-100.0] | **97.0%** [91.55-98.97] | 100.0% | 97.0% | 0.0% | 0.0% | 34.37 ms |
| **8. Hinglish Code-Mixed Wrapping** | **100.0%** [96.3-100.0] | **92.0%** [85.0-95.89] | 100.0% | 92.0% | 39.0% | 0.0% | 31.88 ms |
| **9. Benign Prefix Padding (>256 Tok)** | **98.0%** [93.0-99.45] | **2.0%** [0.55-7.0] | 0.0% | 0.0% | 21.0% | 0.0% | 46.63 ms |
| **10. Benign Suffix Padding (>256 Tok)** | **94.0%** [87.52-97.22] | **0.0%** [0.0-3.7] | 94.0% | 0.0% | 21.0% | 0.0% | 41.69 ms |
| **11. Sandwich Padding (Evasion Core)** | **95.0%** [88.82-97.85] | **2.0%** [0.55-7.0] | 0.0% | 0.0% | 21.0% | 0.0% | 68.05 ms |

### Exaggerated Safety Control (XSTest v2 Disaggregated Evaluation):

1. **Safe Homonym / Taboo Queries ($N=250$)**:
   - **GuardShield False Refusal Rate (FRR)**: **0.0%** [0.0%, 1.51%]
   - Naive Truncation FRR: 0.0%
   - Regex Keyword Blocklist FRR: 0.0%

2. **Unsafe Contrast Requests ($N=200$)**:
   - **GuardShield Recall on Plain Toxic Requests**: **0.0%** [0.0%, 1.88%]
   - *Architectural Note*: GuardShield Stage 1 is specialized as a prompt injection and jailbreak detector, not a general toxicity moderator. It correctly achieves 0.0% false refusals on safe homonyms while passing non-injection toxic queries to upstream policy/generative moderators.
