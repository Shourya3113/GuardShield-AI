# Closest September 2026 preprints vs. planned Paper 1: what was read in full, and how it compares

Read on 2026-10-13. I downloaded all three papers from arXiv (abs, HTML and PDF) and read each one in full, from the title through the last appendix:
- 2609.26176, version v2 (24 Sep 2026)
- 2609.15017, version v1 (14 Sep 2026)
- 2609.01046, version v1 (1 Sep 2026)

Numbers come from the PDF text, because the arXiv HTML render removed most inline math values. Where the PDF table layout was ambiguous (PIDS-Bench Table 7), I checked the cell alignment against the HTML table.

**Not read:**
- the PIDS-Bench GitHub repository
- the HiveTraceGuard-Pro Hugging Face model card
- the code supplement for 2609.26176

**Metadata oddity:** the arXiv abs page for 2609.26176 lists v1 as "Wed, 12 Aug 2026", even though the identifier has a September (2609) prefix. I recorded this as it appears and did not try to explain it ([abs page](https://arxiv.org/abs/2609.26176)).

Planned Paper 1 claims used for the comparison:
- **(1) Protocol.** Paired, length-matched benign twins get the identical label-blind perturbation. The families are zero-width, soft hyphen, leetspeak, Cyrillic homoglyph, and Base64/ROT13 with scaffold controls. Held-out families are fullwidth, combining diacritics and letter spacing.
- **(2) Metrics.** Paired joint accuracy; within-condition AUROC; FPR after re-thresholding each condition to the clean TPR, which separates a "shifted" score distribution from a "destroyed" one.
- **(3) Cross-guard audit.** About 15 open guards, showing two failure modes: fail-closed and fail-open.
- **(4) Language benchmark.** A native-speaker Hindi / romanized Hindi / Hinglish benchmark for over-defense, with fairness metrics.
- **(5) Mitigation.** Canonicalization compared with benign-twin augmentation, on seen and held-out families.

---

## Q1. arXiv 2609.26176, "Refusing Everything Looks Safe: Restoring the Benign Arm to Encoded-Prompt Evaluation" (Northeastern, v2, 24 Sep 2026)

### Takeaway
This paper tests generative chat LLMs: whether they refuse harmful or benign JailbreakBench requests. It does not evaluate any detector, guard or classifier.

It does, however, already contain three of Paper 1's methodological ideas, in an LLM-refusal setting:
- a benign arm passed through the same encoding as the harmful arm;
- a "scaffold" arm (the attack template wrapped around untransformed text) that separates the effect of the template from the effect of the characters;
- a two-arm metric, the "harm gap".

It also says explicitly that the same missing cell exists for prompt guards. It runs no guard experiment.

### Cited Findings

**Design**
- Four 7–8B open models: Llama-3.1-8B-Instruct, Qwen2.5-7B-Instruct, Mistral-7B-Instruct-v0.3 and Tülu-3-8B. The Tülu 3 SFT, DPO and RLVR checkpoints (identical base weights) are used for the pipeline study. Greedy decoding, each model's own chat template, no system prompt. — [arXiv 2609.26176 §3, App. A](https://arxiv.org/pdf/2609.26176)
- Corpus: JailbreakBench's 100 harmful behaviours and 100 theme-matched benign counterparts, paired by name (e.g. jbb_defamation with benign_defamation); n=100 per cell. The pairs are matched by theme, not by length. The paper's own defect (5) reports that "Raw character length alone separates the harmful from the benign corpus at AUROC 0.654 (86.0 vs 73.8 characters)". Length-stratified permutation moves the gap by at most 0.024. — [§3; App. D.3](https://arxiv.org/pdf/2609.26176)
- Arms: each model sees six cells, {harmful, benign} × {plaintext, scaffold, encoded}. Quote: "Scaffold is the cell that separates the two: the same template around untransformed content, so that nothing in it is obfuscated… The scaffold arm is what splits them, it costs one forward pass, and we recommend it as standard." — [§3](https://arxiv.org/pdf/2609.26176)
- Verbatim scaffold template: "The following request is encoded with Cyrillic and Greek homoglyph substitution:" followed by the ciphertext. The fullwidth and zero-width templates change only the naming clause. — [App. A](https://arxiv.org/pdf/2609.26176)
- Encodings:
  - **Homoglyph** (21 Latin characters mapped to Cyrillic, length-preserving) is the main one.
  - **Fullwidth** (U+FF01 offset, space to U+3000) and **zero-width** (U+200B after every character, which roughly doubles length) are used in the pipeline study.
  - **Math-bold** is a second encoding that passes both screens.
  - Seven "rungs" were screened. Quote: "base64 and tag-block are unreadable everywhere and fullwidth, fullwidth-letters and zero-width fail the echo screen on three models each."
  - No leetspeak, ROT13, soft hyphen, combining diacritics or letter spacing.
  - [App. A; Table 2 caption](https://arxiv.org/pdf/2609.26176)
- Refusal is judged by gpt-5-mini at temperature 0, using JailbreakBench's refusal template extended to count echo or irrelevant replies as refusals. Two cross-family LLM annotators validated it on 200 items, with 0.90–1.00 agreement per stratum. — [App. A, E.2](https://arxiv.org/pdf/2609.26176)

**Metric**
- Harm gap: Δ = r_harmful − r_benign within one condition. Also "gap lost = Δplain − Δenc". Quote: "Neither is computable from an attack benchmark: both need the benign arm and the plaintext baseline." Cross-model spreads are read against a bootstrap noise null (20,000 draws, paired on items where available). — [§3](https://arxiv.org/pdf/2609.26176)

**Results**

Table 1 (homoglyph, cross-model):

| Model | Plaintext harmful / benign | Plaintext Δ | Homoglyph harmful / benign | Homoglyph Δ |
|---|---|---|---|---|
| Llama-3.1-8B | 0.92 / 0.10 | +0.82 | 0.99 / 0.99 | 0.00 |
| Qwen2.5-7B | 0.92 / 0.11 | +0.81 | 0.91 / 0.30 | +0.61 |
| Tülu-3-8B | 0.95 / 0.16 | +0.79 | 0.93 / 0.48 | +0.45 |
| Mistral-7B-v0.3 | 0.38 / 0.01 | +0.37 | 0.91 / 0.63 | +0.28 |

- Spread across the four models: harmful-arm spread falls from 0.57 (plaintext) to 0.08 (homoglyph); benign-arm spread rises from 0.15 to 0.69. — [Table 1](https://arxiv.org/pdf/2609.26176)
- Gap collapse is significant on 3 of 4 models: Llama +0.82 [+0.74, +0.90], Tülu +0.34, Qwen +0.20; Mistral +0.09 [−0.06, +0.24] includes zero. — [§4](https://arxiv.org/pdf/2609.26176)
- Second encoding (math-bold) does not replicate the first: Llama Δ is +0.18 under math-bold against 0.00 under homoglyph. Quote: "'encoding destroys the harm gap' as a statement about encodings in general is what the second rung declines to support." — [Table 2, §4](https://arxiv.org/pdf/2609.26176)
- Template vs. characters (Table 3): on Llama the scaffold alone moves benign refusal from 0.10 to 0.83 (Δ +0.83 → +0.16). The template term is +0.67 of a total +0.84. On Qwen the template term is +0.02 and the character term +0.25. Quote: "Which term dominates is a property of the model." — [§5, Table 3](https://arxiv.org/pdf/2609.26176)
- Pipeline (Tülu SFT → DPO → RLVR, Table 4):
  - Plaintext Δ rises from +0.55 to +0.80.
  - Homoglyph Δ rises from +0.20 to +0.46 (paired bootstrap +0.26, 95% CI [+0.14, +0.38]).
  - Gap lost stays at 0.35 → 0.34.
  - Harmful-arm refusal moves 0.99 → 0.94, which does not resolve (McNemar p = 0.06).
  - [§6](https://arxiv.org/pdf/2609.26176)
- Twelve instrument defects. One example: the binary jailbreak judge fires on 0.61–0.70 of responses to plaintext benign prompts. Quote: "Six of the twelve inflate apparent safety." — [§7, App. D](https://arxiv.org/pdf/2609.26176)

**Mitigation**
- No mitigation is proposed: no canonicalization, no augmentation, no training. The only "remedy" studied is an existing published post-training pipeline (Tülu 3). The recommendation is purely about evaluation: "We recommend that encoded-attack evaluations report both arms as a matter of course." — [§6, §9](https://arxiv.org/pdf/2609.26176)

**Detectors and classifiers**
- None are evaluated. The defence side is mentioned only in related work. Quotes: "Fairoze et al. (2026) bypass production prompt guards with encodings a guard cannot decode, and calibrate against untransformed content. A defence whose false-positive rate is measured on plain benign prompts has not measured its false-positive rate under the condition it is deployed against… it is the same missing cell one level out, on the defence rather than the target." — [§2](https://arxiv.org/pdf/2609.26176)
- The literature survey (Table 6) adjudicates 11 transformation-attack papers plus XSTest and OR-Bench. Only Handa et al. (2025) reaches "B3" (benign content through the transformation with a refusal/FP rate). Handa et al. reframe 50 AdvBench items as safe, pass them through five ciphers, and report up to 0.40 incorrectly flagged as unsafe on gpt-oss-20b. — [App. B](https://arxiv.org/pdf/2609.26176)

**Stated limitations**
- One encoding carries the cross-model result.
- The echo screen is outcome-correlated (r = −0.49).
- n=100 cannot separate differences below about 0.15.
- Greedy runs repeat only 12–58% byte-identically.
- Equalisation vs. saturation is unresolved.
- Whether harm information is lost or unused is open; the probe result was withdrawn.
- "Nothing here is held out": every threshold and rung was selected on the same 200 items.
- 7–8B models only.
- [§8, App. E.2, F](https://arxiv.org/pdf/2609.26176)

### Inferences
- **Biggest novelty risk for Paper 1:** the "scaffold" control and the "benign arm through the identical transformation" idea are already published under those names, for LLM refusal. Paper 1 should cite this paper and present its own scaffold arm as carrying that control over to detectors, not as a new invention.
- Paper 1 still has a clear lead on the detector side. This paper explicitly flags the detector-side cell as unmeasured ("the same missing cell one level out") and runs no guard. Paper 1 can quote that sentence as motivation.
- **Paper 1 adds over this paper:**
  - Length matching. This paper uses theme-matching and documents a length AUROC confound of 0.654.
  - Per-item paired twins, so a joint accuracy is possible. This paper's arms are different prompt sets, so its gap intervals are unpaired.
  - Threshold-based metrics (AUROC, re-thresholding). Refusal is binary and has no score.
  - Multiple perturbation families, with held-out families.
  - Mitigation.
- The harm gap is conceptually close to Paper 1's paired joint accuracy (both need both arms). It is a difference of marginal rates, though, not a per-pair joint event.

### Gaps
- The 2609.26176 code supplement and the per-paper verdict appendix were not separately inspected beyond the PDF appendix.
- Fairoze et al. (USENIX Security 2026, "Bypassing Prompt Guards in Production with Controlled-Release Prompting") and Uysal et al. 2026 ("An Empirical Evaluation of Prompt Injection Vulnerabilities Across Multilingual and Obfuscated Attack Scenarios") are cited here as defence-side or multilingual-obfuscation work. I did not read them. They may be relevant competitors.

---

## Q2. arXiv 2609.15017, "PIDS-Bench: Evaluating Prompt-Injection Detectors Under Over-Defense, Obfuscation, and Distribution Shift" (Kookmin Univ.; IEEE Access vol. 14, pp. 134184–134205, 2026)

### Takeaway
PIDS-Bench is a detector-level, English-only, single-turn benchmark with fixed thresholds. It covers seven detectors plus a rule baseline.

Its obfuscation axis contains attacks only, so obfuscated benign text never exists in the benchmark, and it states plainly that "benign FPR is undefined" there. The obfuscated set is leetspeak, homoglyph and zero-width, and those families are already in training.

The closest thing it has to benign-side perturbation is a structural-shift set: JSON wrap, prompt dilution and instruction-prefix mimicry applied to both benign and injection seeds, which are not paired. There:
- deepset DeBERTa-PI flags 100% of benign inputs;
- fine-tuned DeBERTa-v3 flags 0.81 of benign inputs.

It reports Prompt Guard 2 obfuscated recall of 0.3235. Prompt Guard 2's in-distribution recall is already only 0.369, so this is not an obfuscation-specific collapse. The paper never uses the term "fail-open".

### Cited Findings

**Detectors**
- Internal (trained on PIDS): TF-IDF+LR, DistilBERT and DeBERTa-v3-FT, five seeds each.
- External prompt-injection detectors: ProtectAI deberta-v3-base-prompt-injection-v2 and deepset deberta-v3-base-injection ("DeBERTa-PI").
- Broad-safety comparators: Llama Prompt Guard 2 (86M) and Llama Guard 3-1B.
- Plus a keyword/regex rule-based lower bound.
- External and broad-safety detectors run at the default 0.5 boundary. ProtectAI and DeBERTa-PI also get a diagnostic validation-tuned row (τ=0.002 and τ=0.986).
- [§4.1, §4.3](https://arxiv.org/pdf/2609.15017)
- No PIGuard, Prompt Guard v1, Llama Guard 4, Qwen3Guard, WildGuard or perplexity filter. WildGuard and PIGuard are cited only in related work. — [§2.2](https://arxiv.org/pdf/2609.15017)

**Obfuscation families**
- The obfuscated stress set has 405 rows, all injections, drawn from the held-out test split. Quote: "collect the 405 held-out injection examples carrying a character-level obfuscation: leetspeak keyword substitution, homoglyph replacement, or zero-width insertion. These transform families already appear in training, so the set measures sensitivity to known perturbations rather than robustness to novel evasion." — [§5.6d](https://arxiv.org/pdf/2609.15017)
- Base64, ROT13 and "Unicode substitution" appear only as the definition of the `encoded_attack` attack subtype (9% of the injection pool, Table 1). They are not a benign-side or controlled perturbation. Per-subtype recall on `encoded_attack` is 0.999 (DeBERTa-v3-FT) and 1.000 (DistilBERT), reported for internal models only (Table 14). — [Table 1, App. A.2](https://arxiv.org/pdf/2609.15017)
- No soft hyphen, fullwidth, combining diacritics, letter spacing, or wrapper/scaffold controls for encodings.

**Does benign obfuscated text exist? No.**
- Table 3 lists the obfuscated attack set as "100/0" injection/benign.
- The "undefined" statement, in full context, from §4.4 (metrics defined per evaluation setting): "c: Obfuscated attacks stress set. Attack recall is the primary metric. This set contains only injection examples; benign FPR is undefined." The parallel statement for the hard-benign set: "This set contains only benign examples; attack recall is undefined."
- [§4.4, Table 3](https://arxiv.org/pdf/2609.15017)

**Structural-shift set (the only label-blind perturbation applied to benign text)**
- 1,998 rows: three transforms applied to 333 benign seeds (drawn from the hard-benign set) and 333 GPT-4o-mini injection seeds. The transforms are json_wrap, prompt_dilute and instruction_prefix_mimic.
- Benign and injection seeds are separate sets, not paired twins. Quote: "semantic preservation was checked during construction but not independently annotated." — [§5.6c, §8g](https://arxiv.org/pdf/2609.15017)

**Structural-shift FPR results**

| Detector | Structural-shift FPR | Source |
|---|---|---|
| DeBERTa-v3-FT | 0.8108 ± 0.0617 | Table 6 |
| DistilBERT | 0.7826 ± 0.0963 | Table 6 |
| TF-IDF+LR | 0.7918 | Table 6 |
| ProtectAI (default / tuned) | 0.4525 / 0.6647 | Table 7 |
| DeBERTa-PI (default and tuned) | 1.000 / 1.000 | Table 7 |
| Prompt Guard 2 | 0.3323 | Table 7 |
| Llama Guard 3-1B | 0.2222 | Table 7 |

- Per transform for DeBERTa-v3-FT: instruction-prefix 0.918 ± 0.071, dilution 0.796 ± 0.095, JSON 0.719 ± 0.054. — [Table 6, Table 7 (HTML cell alignment checked), §7.4](https://arxiv.org/html/2609.15017)
- Quote: "DeBERTa-PI flags every structural-shift benign input (FPR = 1.000) at both [thresholds]." — [§6.1c](https://arxiv.org/pdf/2609.15017)

**Prompt Guard 2 row (Table 7, native boundary)**

| Detector | IID F1 | IID recall | Hard-benign FPR | Obfuscated recall | Domain-shift F1 | Structural-shift FPR | ROC-AUC |
|---|---|---|---|---|---|---|---|
| Prompt Guard 2 | 0.5390 | 0.369 | 0.1515 | 0.3235 | 0.1900 | 0.3323 | — |
| Llama Guard 3-1B | 0.5692 | 0.420 | 0.1800 | 0.4840 | 0.7923 | 0.2222 | — |

- ROC-AUC is "omitted for PromptGuard 2 and Llama Guard 3-1B, which emit categorical verdicts". There is no per-transform breakdown for Prompt Guard 2.
- The authors read low Prompt Guard 2 and Llama Guard recall as general weakness, not as obfuscation-specific failure. Quote: "The two broad-safety classifiers act as weak injection detectors without adaptation… recalling under half of injections."
- [Table 7, §6.1c](https://arxiv.org/html/2609.15017)
- No "fail-open" or "fail-closed" terminology, and no condition reported with recall going to 0 alongside 0% FPR.

**Other results**
- ProtectAI at default: hard-benign FPR 0.216, obfuscated recall 0.906. At τ=0.002: 0.322 and 0.965. DeBERTa-PI: hard-benign FPR 0.804, obfuscated recall 0.970. — [Table 7](https://arxiv.org/html/2609.15017)
- Hard-benign over-defense (1,472 benign-only prompts: 872 externally sourced, 600 curated). DeBERTa-v3-FT has IID F1 0.9882 but externally-sourced hard-benign FPR 0.3144. No internal model reaches F1 ≥ 0.95 together with externally-sourced FPR ≤ 0.10 at any threshold or seed; the minimum externally-sourced FPR is 0.226 ± 0.058 for DeBERTa-v3-FT. — [Abstract, §6.2, Table 9](https://arxiv.org/pdf/2609.15017)
- Threshold and calibration analysis:
  - A full threshold sweep, an oracle threshold, and temperature scaling (T = 2.02 for DeBERTa-v3-FT).
  - Quote: "no monotonic recalibration can relocate the over-blocked inputs at all", because 32.1% of hard-benign inputs score ≥ 0.9.
  - This is a global "decision surface vs calibration" argument on the hard-benign set. It does not re-threshold per perturbation condition.
  - [§6.2, §6.5c, §6.6](https://arxiv.org/pdf/2609.15017)

**Hard-negative mitigation**
- 419 curated security-adjacent benign examples added to training. No perturbation-based augmentation.
- Results (Table 10, five-seed means):
  - Curated FPR falls sharply: DeBERTa-v3-FT 0.4813 → 0.0010; DistilBERT 0.4843 → 0.0123.
  - Externally-sourced FPR barely moves: DeBERTa 0.3144 → 0.3101 (paired Δ −0.004, p = 0.90); DistilBERT 0.4606 → 0.3899.
  - Small domain-shift F1 cost: 0.9604 → 0.9473.
  - Pool sizes {100, 200, 300, 419} show no trend.
  - The authors call this "provenance-sensitive over-defense".
- No obfuscated-benign or held-out-obfuscation mitigation results.
- [§6.3, Table 10, Table 12, Fig. 3](https://arxiv.org/pdf/2609.15017)

**Open problems listed (§7.6, §8)**
- augmentation matched to the externally-sourced distribution;
- leave-one-source-out retraining;
- generalisation "to obfuscation strategies absent from training, such as semantic paraphrase or multi-step encoding";
- probing or attribution of the transformers;
- thresholds conditioned on provenance or structure (with the risk of opening an evasion channel);
- isotonic or Bayesian calibration;
- multilingual and multi-turn extension.
- Quote: "The benchmark is further restricted to single-turn, English-language inputs."
- [§3.5, §7.6, §8a](https://arxiv.org/pdf/2609.15017)

**Release**
- Frozen splits with SHA-256 manifest at github.com/ShirePyDev/Prompt-Injection-Detection-System, tag v1.0-pids-bench (commit 87dc835). — [Data Availability](https://arxiv.org/pdf/2609.15017)

### Inferences
- **Novelty is intact for Paper 1:**
  - No benign obfuscated twins.
  - No paired joint accuracy.
  - No within-condition AUROC for obfuscation. AUROC is reported only overall, and not for Prompt Guard 2 or Llama Guard.
  - No re-thresholding per condition to the clean TPR.
  - No canonicalization.
  - No held-out obfuscation families.
- Paper 1 can cite PIDS-Bench's own wording ("benign FPR is undefined") as direct evidence of the gap it fills.
- **Partial overlaps to acknowledge:**
  - The structural-shift set does apply wrapper-type transforms to benign text. DeBERTa-PI's FPR of 1.000 there is a published "fail-closed" observation for deepset under benign structural wrapping (not character perturbation).
  - The §6.6 "monotone recalibration cannot fix it" reasoning is a precedent for Paper 1's shifted-vs-destroyed logic, but it runs in the over-defense direction and globally, not per perturbation condition.
- **Prompt Guard 2's 0.32 obfuscated recall does not anticipate Paper 1's fail-open finding.** It sits beside 0.369 in-distribution recall at the categorical native boundary, with no per-family breakdown, no soft hyphen and no Base64 cell. Paper 1's claim (recall drops to 0% under specific families while FPR stays at 0%) is a different, more specific result.
- The detector overlap with Paper 1's ~15-guard list is ProtectAI v2, deepset, Prompt Guard 2 and Llama Guard 3 (1B only). PIDS is not a broad cross-guard audit.

### Gaps
- I did not inspect the GitHub artifact, so I could not check whether per-transform obfuscation results for Prompt Guard 2 or the external detectors exist in released prediction files.
- The paper gives no per-family (leet / homoglyph / zero-width) obfuscated recall for any detector.

---

## Q3. arXiv 2609.01046, "HiveTraceGuard-Pro: A Compact Generative Guardrail for Prompt Injection, Jailbreaks, and Adversarial Obfuscation" (HiveTraceLab, 1 Sep 2026)

### Takeaway
This is a model paper: a 0.6B Qwen3 LoRA guard for Russian and English.

Its training corpus pairs harmful examples with topic-matched benign examples and applies eight obfuscation transforms to both labels. Its Russian robustness test set likewise crosses "paired safe/harm twins" with eight transforms. That makes it the closest existing precedent for Paper 1's "perturb the benign twin too" design.

But:
- the transforms are Russian-oriented (keyboard layout, transliteration, case, symbol insertion) and exclude Base64, ROT13, homoglyph and soft hyphen;
- per-transform benign FPR (Table 13) is reported for its own model only;
- the twins are topic-paired, not length-matched;
- the metrics are F1/FPR/FNR at a fixed boundary, with no joint accuracy, no per-condition AUROC and no per-condition re-thresholding;
- there is no normalizer;
- there is no Hindi.

Its main finding is a recall/FPR coupling under obfuscation that six data rounds could not break.

### Cited Findings

**Model and data**
- Qwen3-0.6B with LoRA (rank 64), binary safe/unsafe verdict token. 464,092 training rows: 59.7% Russian, 41.5% unsafe.
- Weights released under Apache-2.0. The corpus, evaluation sets and evaluation code remain internal.
- [Abstract, §3.2, Table 8, Table 10](https://arxiv.org/pdf/2609.01046)

**Pairing and two-sided obfuscation**
- Quote: "Its training corpus pairs harmful examples, where a counterpart exists, with benign examples from the same domain and applies eight obfuscation transforms to both labels."
- The pairing is semantic or topical, e.g. "Fascism versus History of fascism or Drugs versus Pharmacology". No length matching is described.
- [Abstract, §4.1](https://arxiv.org/pdf/2609.01046)

**Training transforms (Table 9)**
- The eight transforms: random_case, random_insert_symbols, random_replace_symbols, zero_width_insert, leet, transliterate_to_latin, wrong_layout (kbd_layout_swap) and phonetic_substitution. Quote: "None of the eight transforms listed here is withheld from training."
- 38,729 obfuscation rows were added by augmentation; 47,421 mechanical obfuscation rows in total by provenance.
- [Table 9, App. A.1, A.5](https://arxiv.org/pdf/2609.01046)

**Evaluation transforms (Table 13)**
- Eight transforms on requests only: to_lower, to_upper, random_case, random_insert_symbols, random_replace_symbols, transliterate_to_latin, wrong_layout, informal_rewrite.
- The evaluation-only (held-out) transforms are to_lower, to_upper and informal_rewrite.
- leet, zero_width_insert and phonetic_substitution are "trained but not evaluated".
- Each transform cell has 342–345 harmful and 449–450 benign rows (Russian robustness-test).
- [Table 13 caption, §3.1](https://arxiv.org/pdf/2609.01046)
- No Base64, ROT13, Cyrillic homoglyph, soft hyphen, fullwidth, combining diacritics or letter spacing. The system-prompt policy text mentions "Obfuscation: leet/base64 hiding request", but Base64 is not among the transforms. — [App. B.1](https://arxiv.org/pdf/2609.01046)

**Table 13, per-transform request-side results (released model)**

| Transform | Harm-F1 | FPR | FNR | Notes |
|---|---|---|---|---|
| Clean | 0.889 | 0.016 | 0.041 | |
| to_lower | 0.955 | 0.033 | 0.046 | held out |
| to_upper | 0.863 | 0.173 | 0.070 | held out |
| random_case | 0.816 | 0.193 | 0.136 | |
| random_insert_symbols | 0.896 | 0.084 | 0.099 | |
| random_replace_symbols | 0.860 | 0.127 | 0.122 | |
| transliterate_to_latin | 0.879 | 0.131 | 0.081 | |
| wrong_layout | 0.790 | 0.262 | 0.125 | |
| informal_rewrite | 0.756 | 0.107 | 0.307 | held out |
| Responses, clean | 0.671 | 0.043 | 0.180 | |

- Quote: "Every transform worsens at least one error rate relative to clean requests." — [Table 13, Fig. 3](https://arxiv.org/pdf/2609.01046)

**Recall/FPR coupling**
- Quote: "Across the additive rounds in Section G, improvements on one obfuscation error rate repeatedly worsened the other. None of the tested data mixtures removed this coupling. Because all experiments keep the model at 0.6B, they do not distinguish a data limitation from a capacity limitation." — [§4.5](https://arxiv.org/pdf/2609.01046)
- Limitations: "Across six additive data rounds and one change of training objective, improvements in recall on obfuscated harmful requests repeatedly increased over-blocking of obfuscated benign requests, or the reverse." — [§6](https://arxiv.org/pdf/2609.01046)
- Specific instances:
  - Rebalancing changed wrong_layout harm-FNR 0.061 → 0.125 while FPR went 0.358 → 0.262.
  - An over-refusal round cut wrong_layout FPR 0.262 → 0.222 and OR-Bench-hard FPR 0.61 → 0.20, but raised obfuscated-harm FNR 0.097 → 0.116 (Holm p < 0.01), so it was not adopted.
  - Removing two-sided (assistant-side) obfuscation "regressed on 7 of 8 augmented-benign conditions".
  - Removing keyboard-layout augmentation raised wrong_layout FNR 0.357 → 0.626.
  - A cipher mismatch between training and evaluation gave a pre-fix wrong_layout FNR of 0.675.
  - [App. G, §4.5](https://arxiv.org/pdf/2609.01046)

**Normalization**
- Quote: "The shipped path has no input normalizer, and reported labels are direct model outputs." — [§4.1](https://arxiv.org/pdf/2609.01046)
- The only "normalization" in the paper is corpus normalization to a common dialogue format, and "normalizing the sampling rate of each obfuscation transform". No text canonicalization is studied. — [App. A.3, App. G](https://arxiv.org/pdf/2609.01046)

**Thresholding and AUROC**
- Decision rule: argmax, equivalent to a 0.5 boundary, "not calibrated separately by language". — [§4.1](https://arxiv.org/pdf/2609.01046)
- AUROC is reported only as aggregates: 0.997 on clean requests, 0.985 on RU-categories, 0.973 on pooled robustness rows, 0.888 on Aegis-2.0. There is no per-transform AUROC. — [§4.3, §5](https://arxiv.org/pdf/2609.01046)
- A global threshold sweep finds τ = 0.532, with Δ macro-F1 < 0.001. — [§5](https://arxiv.org/pdf/2609.01046)

**Cross-guard comparison**
- A suite of 35 guards on 19 benchmark groups (44 datasets), aggregate key = geometric mean. — [§4.1, Table 11](https://arxiv.org/pdf/2609.01046)
- The suite includes:
  - Llama-Prompt-Guard-2-86M (key 0.0006) and 22M (< 0.0001)
  - deberta-v3-base-prompt-injection-v2 (ProtectAI, 0.0003)
  - deberta-v3-base-injection (deepset, 0.0068)
  - "promptguard" (0.3460)
  - Llama Guard 3-1B, 3-8B and 4-12B; Qwen3Guard-Gen 0.6B/4B/8B; WildGuard; ShieldGemma; and others
- Pooled over the suite: "Three injection-focused detectors fall outside the plotted range, at FPR 0.776, FPR 1.000 and FNR 0.989". They are not named. — [Table 11, Fig. 4](https://arxiv.org/pdf/2609.01046)
- Cross-guard robustness to obfuscation appears only as a pooled "Robust-in" column (augmented Russian requests, all 8 transforms pooled) for the 15-guard cohort:

| Guard | Robust-clean FPR | Robust-in FPR / FNR |
|---|---|---|
| HiveTraceGuard-Pro | .02 | .13 / .13 |
| Llama-Guard-4-12B | .07 | .24 / .16 |
| Llama-Guard-3-1B | .09 | .13 / .27 |
| Qwen3Guard-Gen-8B | — | .05 / .15 |

- Prompt Guard 2 and ProtectAI are not in that cohort table.
- [Table 2](https://arxiv.org/pdf/2609.01046)

**Multilingual evaluation**
- Russian and English only. Internal Russian sets: robustness-test, RU-categories, RU prompt injection (attack-only; 27.1% overlap with training), and the reserved insecure-prompts set. — [Table 1, App. A.4](https://arxiv.org/pdf/2609.01046)
- Multilingual public slices: Aya Red-teaming RU/EN, RTP-LX RU/EN, XSafety; the suite also includes PolyGuard, MultiJail, CSRT (code-switching) and StrongREJECT++ language slices. — [Table 5, App. C](https://arxiv.org/pdf/2609.01046)
- Quote: "The model is not validated for languages other than Russian and English." No Hindi or Hinglish, and no fairness or parity metrics. — [§5](https://arxiv.org/pdf/2609.01046)

**Stated limitations**
- Over-blocking is more common than misses: suite FPR 0.268, FNR 0.156.
- Response side is weak (reserved-set response FPR 0.563).
- The obfuscation trade-off is unresolved.
- No truncation; a harmful request under about 80k filler tokens was labeled safe.
- Response results use a legacy standalone-reply serialization.
- Single runs, no cross-model confidence intervals.
- Internal, contaminated sets.
- [§6, §5, App. A.4](https://arxiv.org/pdf/2609.01046)

### Inferences
- **The strongest prior art for Paper 1's claim (1) and claim (5) intuition.** "Apply the obfuscation to both labels" of a topic-paired twin corpus is published, both as training augmentation (comparable to Paper 1's benign-twin augmentation arm) and as an evaluation set with per-transform benign FPR. Paper 1 must cite it and set itself apart on four points:
  - **Detector auditing.** HiveTrace's per-transform table covers its own model only; Paper 1 audits about 15 third-party guards per family.
  - **Twin construction.** Paper 1 uses identical, length-matched, per-item twins; HiveTrace uses topic pairs.
  - **Perturbation families.** Paper 1's families are encoding and Unicode based (Base64/ROT13 with scaffolds, soft hyphen, homoglyph, fullwidth, combining marks); HiveTrace's are keyboard layout, transliteration and case.
  - **Metrics.** Paper 1 uses joint accuracy, per-condition AUROC and re-thresholding to the clean TPR.
- HiveTrace's recall/FPR coupling result is a useful foil. Paper 1's re-threshold-to-clean-TPR metric can test whether such a coupling is a threshold shift (fixable) or a loss of ranking signal. HiveTrace reports no per-transform AUROC, so it cannot tell the two apart.
- HiveTrace includes no canonicalizer and reports augmentation only. Paper 1's canonicalization-vs-augmentation comparison (claim 5) is not covered. HiveTrace's results do suggest augmentation alone produces a trade-off, which supports running the comparison.
- The unnamed pooled "FPR 1.000" and "FNR 0.989" injection detectors in Fig. 4 resemble Paper 1's fail-closed / fail-open dichotomy at the level of a whole suite. They are not tied to perturbations, so Paper 1's per-family fail-open finding (Prompt Guard 2 recall to 0% with 0% FPR) remains new.

### Gaps
- Table 2 does not report per-transform FPR for other guards. I could not determine whether the internal artifacts hold such data.
- The identities of the three off-plot injection detectors in Fig. 4 are not given.
- I did not read the Hugging Face model card.

---

## Q4. Claim-by-claim coverage matrix (Paper 1 vs. the three preprints)

### Takeaway
None of the three preprints covers any Paper 1 claim in full, but claim (1) is partly covered by two of them:
- 2609.26176 has the benign-arm and scaffold logic, for LLM refusal.
- 2609.01046 has two-sided obfuscation of topic-paired twins, for its own guard.

Claims (2) and (4) are essentially untouched. Claim (3) is partly covered: PIDS-Bench has a small detector set, and HiveTraceGuard-Pro has a pooled 35-guard suite. Claim (5) is partly covered only on the augmentation side.

### Cited Findings

**Claim 1: paired, length-matched benign twins with identical label-blind perturbation; scaffold controls; held-out families**
- 2609.26176 (Refusing Everything) — **Partial (concept), for LLM refusal only.**
  - Benign arm through the same transformation.
  - Scaffold arm: "the same template around untransformed content" ([§3](https://arxiv.org/pdf/2609.26176)).
  - Theme-matched JailbreakBench pairs, not length-matched; it documents a length confound at AUROC 0.654 ([App. D.3](https://arxiv.org/pdf/2609.26176)).
  - Encodings: homoglyph, fullwidth, zero-width, math-bold; Base64 dropped as unreadable.
  - No held-out-family design.
  - No detectors.
- 2609.15017 (PIDS-Bench) — **Untouched for character obfuscation; partial for structural.**
  - The obfuscated set is attacks only ("benign FPR is undefined", [§4.4](https://arxiv.org/pdf/2609.15017)).
  - Structural transforms are applied to unpaired benign and injection seeds ([§5.6c](https://arxiv.org/pdf/2609.15017)).
  - Obfuscation families are already seen in training ([§5.6d](https://arxiv.org/pdf/2609.15017)).
- 2609.01046 (HiveTraceGuard-Pro) — **Partial.**
  - "paired safe/harm twins, requests crossed with clean and eight obfuscation transforms" ([Table 1](https://arxiv.org/pdf/2609.01046)), with three evaluation-only transforms ([Table 13](https://arxiv.org/pdf/2609.01046)).
  - Twins are topic-paired, not length-matched.
  - Russian-oriented transforms.
  - No scaffold or wrapper control.
  - Applied to its own model only.

**Claim 2: paired joint accuracy, within-condition AUROC, FPR re-thresholded to clean TPR (shifted vs. destroyed)**
- 2609.26176 — **Partial analogue.** The harm gap Δ = r_harm − r_benign is a two-arm metric, but a difference of marginals with unpaired arms ([§3, defect 12](https://arxiv.org/pdf/2609.26176)). No scores, AUROC or thresholds. The paper itself leaves "lost vs. unused" harm information open ([App. F.1](https://arxiv.org/pdf/2609.26176)), which is close to Paper 1's shifted/destroyed question asked of model internals.
- 2609.15017 — **Untouched as defined.** It has threshold sweeps, an oracle threshold and temperature scaling, showing over-defense is "not a calibration artifact" ([§6.2, §6.6](https://arxiv.org/pdf/2609.15017)). This is on the hard-benign set globally, not per perturbation condition. No joint accuracy, no within-condition AUROC.
- 2609.01046 — **Untouched.** Per-transform F1/FPR/FNR at a fixed argmax ([Table 13](https://arxiv.org/pdf/2609.01046)). AUROC on aggregates only; one global threshold sweep (τ = 0.532) ([§5](https://arxiv.org/pdf/2609.01046)).

**Claim 3: cross-guard audit of about 15 open guards, with fail-closed and fail-open modes**
- 2609.26176 — **Untouched.** No guards. The detector-side cell is mentioned as missing ([§2](https://arxiv.org/pdf/2609.26176)).
- 2609.15017 — **Partial.**
  - Covers ProtectAI v2, deepset, Prompt Guard 2 and Llama Guard 3-1B, plus 3 internal detectors ([§4.1](https://arxiv.org/pdf/2609.15017)).
  - deepset flags 100% of structural-shift benign inputs, a fail-closed-like observation ([§6.1c](https://arxiv.org/pdf/2609.15017)).
  - Prompt Guard 2 obfuscated recall is 0.3235 against IID recall 0.369, with no per-family split and no "fail-open" framing ([Table 7](https://arxiv.org/html/2609.15017)).
- 2609.01046 — **Partial.**
  - 35-guard suite including Prompt Guard 2 (86M/22M), ProtectAI v2, deepset, Llama Guard 3/4, Qwen3Guard and WildGuard ([Table 11](https://arxiv.org/pdf/2609.01046)).
  - Obfuscation appears only as pooled "Robust-in" FPR/FNR for 15 guards ([Table 2](https://arxiv.org/pdf/2609.01046)).
  - Unnamed injection detectors sit at pooled FPR 1.000 and FNR 0.989 ([Fig. 4](https://arxiv.org/pdf/2609.01046)).
  - No per-family audit.

**Claim 4: native-speaker Hindi / romanized Hindi / Hinglish over-defense benchmark with fairness metrics**
- 2609.26176 — **Untouched.** English JailbreakBench only ([App. A](https://arxiv.org/pdf/2609.26176)).
- 2609.15017 — **Untouched.** "single-turn, English-language inputs", with multilingual listed as future work ([§3.5, §7.6](https://arxiv.org/pdf/2609.15017)).
- 2609.01046 — **Untouched for Hindi.**
  - The analogous setting is Russian: a Russian-focused guard with a Cyrillic-to-Latin transliteration transform (FPR 0.131), comparable to romanized script ([Table 13](https://arxiv.org/pdf/2609.01046)).
  - Per-language FPR is reported, e.g. benign-English FPR 0.591 → 0.153 in development ([App. G](https://arxiv.org/pdf/2609.01046)).
  - No fairness metrics.
  - The suite includes CSRT (code-switching) and MultiJail only as aggregate scores ([App. C](https://arxiv.org/pdf/2609.01046)).

**Claim 5: script-aware canonicalization vs. benign-twin augmentation, on seen vs. held-out families**
- 2609.26176 — **Untouched.** No mitigation, only the Tülu post-training pipeline analysis ([§6](https://arxiv.org/pdf/2609.26176)).
- 2609.15017 — **Partial on augmentation only.** Curated hard-negative augmentation, not perturbation twins. It clears curated FPR but not externally-sourced FPR ([Table 10](https://arxiv.org/pdf/2609.15017)). No canonicalization. "obfuscation strategies absent from training" is listed as open ([§7.6](https://arxiv.org/pdf/2609.15017)).
- 2609.01046 — **Partial on augmentation only.**
  - Two-sided obfuscation augmentation, with evaluation on 5 trained and 3 held-out transforms ([Table 9, Table 13](https://arxiv.org/pdf/2609.01046)).
  - A recall/FPR coupling persists across six rounds ([§6, App. G](https://arxiv.org/pdf/2609.01046)).
  - Quote: "The shipped path has no input normalizer" ([§4.1](https://arxiv.org/pdf/2609.01046)).
  - No canonicalization comparison.

### Inferences
- **The novelty case should rest on:**
  - applying paired benign twins to third-party detectors, broadly and per family;
  - the score-level metrics (joint accuracy, per-condition AUROC, re-thresholding to the clean TPR) that can tell shifted signal from destroyed signal;
  - the per-family fail-open finding for Prompt Guard 2;
  - the Hindi/Hinglish benchmark;
  - the canonicalization arm.
- **Wording to soften:**
  - Do not claim the "benign arm under the same transformation" idea or the "scaffold" control as new. 2609.26176 introduces both for LLM refusal and explicitly recommends the scaffold as standard.
  - Do not claim "obfuscate both labels" as new for training or evaluation. 2609.01046 does it for its own guard.
- **Direct citations Paper 1 can use to motivate its gap:**
  - From 2609.26176 §2: "the same missing cell one level out, on the defence rather than the target".
  - From PIDS-Bench §4.4: "benign FPR is undefined".
  - From HiveTraceGuard-Pro §4.5: the coupling statement "improvements on one obfuscation error rate repeatedly worsened the other".

### Gaps
- Not checked: whether Fairoze et al. (USENIX Security 2026), Uysal et al. 2026, or Handa et al. 2025 (CipherBench, safe-reframed AdvBench through five ciphers, FP rate reported) evaluate detectors with benign obfuscated text. Each is cited in 2609.26176 and may matter for claims 1 and 3.
- I inspected no released artifacts (PIDS GitHub, HiveTrace HF card), so any per-family detector numbers that exist only in data releases are not covered here.
