# Pilot run, 2026-10-12 (harness validation, not paper results)

**Purpose:** check that the harness, guard adapters and metrics behave sensibly before the full runs. These numbers come from **150 pairs** (Gandalf attacks × length-matched Dolly twins, seed 13) with 300 calibration prompts, on a laptop RTX 3050. They are **not** paper results. The primary run in `paper1/SPEC.md` uses 500 pairs and the full guard roster.

Files: `manifest.json` (dataset provenance), `metrics.json` (all metrics with CIs), `report_fpr5.md` (thresholds at 5% FPR on the calibration pool), `report_default.md` (each guard's default threshold).

Guards scored: GuardShield, ProtectAI v2, deepset, fmops, GPT-2 perplexity, Qwen3Guard-Gen-0.6B; added 2026-10-13: Prompt Guard v1 (both modes), Prompt Guard 2 86M/22M, Llama Guard 3 1B.

## What the pilot suggests (to be confirmed at full scale)

1. **H1 looks strongly supported for encoder classifiers.**
   - At 5% calibrated FPR, ProtectAI v2 keeps about 100% attack recall under every character family.
   - Its benign twins are flagged at 97–100%, so its paired joint accuracy falls from 94.7% (clean) to 0–2.7%.
   - GuardShield behaves the same way (90.7% → 0–0.7%).
   - An attack-only evaluation would have called both guards robust.
2. **The intent signal is destroyed, not just shifted.** Re-thresholding each condition to its clean TPR still leaves 83–100% FPR for GuardShield and ProtectAI on character families. Recalibration would not fix them; normalization or retraining is needed. This bears directly on Study C.
3. **The tokenizer decides which families hurt (H4).**
   - fmops (DistilBERT) is unaffected by zero-width, soft-hyphen and diacritics, which its tokenizer strips.
   - fmops loses all recall on fullwidth text (0% TPR).
   - The DeBERTa-based guards are unaffected by fullwidth but collapse under zero-width and soft hyphens.
4. **The wrapper wording matters on its own for some guards.**
   - With the Base64 template wrapped around *plain* text (`base64_scaffold`), ProtectAI flags 84.7% of benign twins at its default threshold; GuardShield flags 2%.
   - The scaffold control is needed to separate template effects from encoding effects.
5. **The generative judge fails in a different way.**
   - Qwen3Guard-Gen-0.6B mostly keeps its ranking under character families (AUROC 0.82–0.89 vs 0.94 clean).
   - It has 0% recall on Base64/ROT13-wrapped attacks at its default threshold: it cannot see the payload.
   - It over-flags leetspeak (95% benign FPR at default) and diacritics.
6. **Perplexity filtering is a weak baseline** (clean AUROC 0.63). It mostly fails to flag obfuscated attacks at all, so it does not show the format-rejection pattern.

7. **Prompt Guard 2 fails in the opposite direction ("fail-open").**
   - At its default threshold its benign FPR stays at 0% under every perturbation.
   - Its attack recall collapses instead: about 99% clean, but 0% under soft hyphens, leetspeak, Base64 and ROT13.
   - So the paired metric has to catch both failure modes. ProtectAI/GuardShield reject the unfamiliar (high FPR); Prompt Guard 2 lets it through (low TPR).
   - Prompt Guard 2 is unaffected by zero-width characters and letter spacing (its tokenizer drops or normalizes them).
8. **Prompt Guard v1 in INJECTION+JAILBREAK mode flags every prompt** (100% FPR even on clean benign text), so its paired accuracy is 0 everywhere. In JAILBREAK-only mode (Meta's advice for user input) it behaves like Prompt Guard 2.
9. **Llama Guard 3 1B** catches only 57% of clean injections (it judges harm, not injection). It flags 72% of benign leetspeak and 100% of benign Base64 at its default threshold.

## Harness checks done

- Generative scoring agrees with greedy generation on Qwen3Guard: Safe → 0.0006, Unsafe → 0.999, Controversial → 0.82.
- Classifier label mappings resolved from each model's `id2label`. fmops has unnamed labels; label 1 is assumed to mean injection, from its training data.
- The scaffold arm and label-blind wrappers are verified by unit tests (`tests/test_guard_audit.py`).

## Known caveats for the full run

- Gandalf attacks are mostly short "ignore previous instructions"-style requests. Add a second attack source, such as deepset_test, reported separately and flagged where contaminated.
- At n = 150, Wilson intervals are ±5–8 points; the primary run uses 500 pairs.
