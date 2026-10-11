# GuardShield AI — Adaptive Adversarial Attack & Robustness Benchmark

| Adversarial Attack / Evasion Category | Sample Count | GuardShield AI (Proposed) | Naive Truncation (128 Tok) | Static Keyword Blocklist | GuardShield Latency (p50) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **1. Raw Ingress Injections (Baseline)** | 8 | **100.0%** | 100.0% | 75.0% | 31.8 ms |
| **2. Zero-Width Spaces (Invisible Chars)** | 8 | **100.0%** | 100.0% | 37.5% | 27.79 ms |
| **3. Soft-Hyphens (Subword Splitting)** | 8 | **100.0%** | 100.0% | 37.5% | 42.11 ms |
| **4. Leetspeak Obfuscation** | 8 | **100.0%** | 100.0% | 0.0% | 42.97 ms |
| **5. Cyrillic Homoglyphs (Visual Spoof)** | 8 | **100.0%** | 100.0% | 0.0% | 24.19 ms |
| **6. Base64 Cipher Wrapping** | 8 | **100.0%** | 100.0% | 0.0% | 27.28 ms |
| **7. ROT13 Caesar Cipher Wrapping** | 8 | **100.0%** | 100.0% | 0.0% | 23.41 ms |
| **8. Hinglish Code-Mixed Wrapping** | 8 | **100.0%** | 100.0% | 75.0% | 27.06 ms |
| **9. Benign Prefix Padding (>256 Tok)** | 8 | **100.0%** | 0.0% | 75.0% | 39.48 ms |
| **10. Benign Suffix Padding (>256 Tok)** | 8 | **87.5%** | 87.5% | 75.0% | 39.32 ms |
| **11. Sandwich Padding (Evasion Core)** | 8 | **100.0%** | 0.0% | 75.0% | 77.21 ms |

### Exaggerated Safety & False Positive Control (XSTest v2 Benchmark):

- **Evaluated Samples**: 450 benign prompts containing taboo/sensitive security keywords.
- **GuardShield False Refusal Rate (FPR)**: **0.0%**
- **Naive Truncation False Refusal Rate**: 0.0%
- **Keyword Blocklist False Refusal Rate**: 0.0% *(Keyword matching over-refuses legitimate security queries)*
