# Multilingual competitors: guard false positives on benign Hindi, romanized Hindi and Hinglish

Scope: whether any existing guard model, benchmark or paper already measures false positives of prompt-injection or safety guards on benign Devanagari Hindi, romanized Hindi, or Hindi-English code-mixed (Hinglish) text. Research date: 2026-10-13. "Primary" means the full text or official page was read. "Snippet/abstract-only" is marked where only that was read.

Overall verdict: no source found measures per-register false-positive rates of prompt-injection detectors on benign Hindi in Devanagari, romanized and code-mixed forms. No source found uses FPR-parity or matched-TPR fairness metrics for Indic registers. The closest prior works are Srinivasan et al. 2026, which trains its own detector on machine-translated Hindi and transliterated "Hinglish" (CC0 Kaggle data), and BanglaVeilGuard 2026, which covers cross-script over-refusal for Bangla, not Hindi, and has no fairness metric. Both must be cited and set apart from this work.

## PolyGuard (arXiv 2504.04377) and Qwen3Guard (arXiv 2510.14276): per-language FPR or over-refusal, Hindi numbers, romanized or code-mixed coverage

### Takeaway
Neither paper reports per-language false-positive or over-refusal rates for Hindi. Neither covers romanized Hindi or Hinglish. PolyGuard's Hindi data is machine-translated (NLLB). Qwen3Guard pools Hindi, if present at all, into an "Others" average.

### Cited Findings
- PolyGuard covers 17 languages, Hindi among them (Arabic, Chinese, Czech, Dutch, English, French, German, Hindi, Thai, Italian, Japanese, Korean, Polish, Portuguese, Russian, Spanish, Swedish). Model results are averaged across languages, with no per-language model performance table — [PolyGuard, arXiv 2504.04377 (primary, HTML)](https://arxiv.org/html/2504.04377)
- PolyGuard reports no false-positive or over-refusal rate for any language. Its "response refusal" task asks whether the LLM response refuses the user, not whether the guard wrongly flags benign prompts — [PolyGuard HTML](https://arxiv.org/html/2504.04377)
- PolyGuardMix Hindi is machine-translated from WildGuardMix with NLLB-3.3B because TowerInstruct does not support Hindi. The paper notes Tower's Hindi output was poor. — [PolyGuard HTML](https://arxiv.org/html/2504.04377)
- PolyGuard's only Hindi-specific numbers are about translation and annotation quality:
  - Average translation score of 84.72 out of 100, against a cross-language mean of 81.15.
  - Krippendorff's alpha of 0.34 on the source and 0.37 on the translation.
  - GPT-4o judge on NLLB prompt translations: 1,470 entirely correct, 186 partially correct, 69 bad.
  - Source: Tables 8–10 of [PolyGuard HTML](https://arxiv.org/html/2504.04377)
- PolyGuard evaluates code-switching in general but does not mention Hinglish or romanized Hindi — [PolyGuard HTML](https://arxiv.org/html/2504.04377)
- Qwen3Guard reports per-language F1 only for named languages in Tables 5 and 6 (En, Zh, Ar, Es, Fr, Id, It, Ja, Ko, Ru). It pools the other 30 prompt languages and 8 response languages into an "Others" average. Hindi is not named in any results table. — [Qwen3Guard Technical Report, arXiv 2510.14276 (primary, first ~100k chars of HTML read)](https://arxiv.org/html/2510.14276)
- Qwen3Guard has no FPR or over-refusal table. Table 7 reports refusal-detection P/R/F1 on XSTest and WildGuardTest, which is not a benign false-positive rate. It has no dedicated prompt-injection benchmark ("Jailbreak" is only an input category) and does not mention romanized Hindi or Hinglish. — [Qwen3Guard HTML](https://arxiv.org/html/2510.14276)

### Inferences
- Both flagship multilingual guards leave the Hindi benign false-positive question open. Neither has a per-register breakdown or any injection-specific benign false-positive measurement. The planned benchmark would be the first to give Hindi-register false-positive numbers for these models.
- PolyGuard's Hindi alpha of 0.34 on the source labels is the lowest it reports. That is a useful argument for native-speaker-written seeds over translated ones.

### Gaps
- The last ~19k characters of the Qwen3Guard HTML were not read. An appendix with per-language tables that include Hindi cannot be fully ruled out. The main results tables do not name Hindi.
- Qwen3Guard's full training-language list (said to be 119 languages) was not checked for Hindi.

## Llama Prompt Guard 2: does Meta publish per-language results, including Hindi?

### Takeaway
Meta names Hindi among the evaluated languages but publishes only one aggregate "AUC (Multilingual)" figure. It gives no per-language numbers, no Hindi FPR, and no recall at fixed FPR for the multilingual set. The multilingual set is machine-translated English data.

### Cited Findings
- The Prompt Guard 2 model card says the models were evaluated for attack detection in English, French, German, Hindi, Italian, Portuguese, Spanish and Thai. — [HF model card, meta-llama/Llama-Prompt-Guard-2-86M (primary)](https://huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M)
- Reported numbers:

  | Model | AUC (English) | Recall @ 1% FPR (English) | AUC (Multilingual) |
  |---|---|---|---|
  | Prompt Guard 1 | .987 | 21.2% | .983 |
  | Prompt Guard 2 86M | .998 | 97.5% | .995 |
  | Prompt Guard 2 22M | .995 | 88.7% | .942 |

  There is no per-language breakdown and no standalone FPR. — [HF model card](https://huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M)
- The 22M model has no multilingual pretraining, and the card notes "a larger performance gap" on multilingual data. — [HF model card](https://huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M)
- The LlamaFirewall paper (Appendix A.2) describes the multilingual set as "the same dataset machine-translated into eight additional languages" without naming them. It reports Recall @ 1% FPR only for English. Section B.2 says only that the 22M model "showed reduced performance in multilingual scenarios", with no number. — [LlamaFirewall, arXiv 2505.03574 (primary, ~100k of 113k chars read)](https://arxiv.org/html/2505.03574)

### Inferences
- Meta's multilingual claim rests on machine-translated Devanagari-style data, with no romanized or code-mixed coverage stated and no benign per-language FPR. Per-register FPR, and FPR at matched English TPR, for Prompt Guard 2 on Hindi registers would be new.
- The English operating point (1% FPR) is a natural anchor for the planned "FPR at matched English TPR" metric.

### Gaps
- It is unclear whether Meta's eight translated languages match the model card's list of 7 non-English languages plus English. The paper says "eight additional", and the card lists 7 non-English languages.

## Horizon-Labs multilingual prompt-injection guard: languages, Hindi, per-language FPR

### Takeaway
Could not be verified. The model appears gated, private or removed, and no secondary source indexes it.

### Cited Findings
- `https://huggingface.co/api/models/Horizon-Labs/prompt-injection-guard-multilingual` and `.../raw/main/README.md` both returned HTTP 401 on 2026-10-13. The public HF search API (`/api/models?search=prompt-injection-guard-multilingual`) returned an empty list `[]`, which suggests the repo is private, gated without public listing, or deleted. — [HF API](https://huggingface.co/api/models/Horizon-Labs/prompt-injection-guard-multilingual)
- Web searches found no mirror, paper or third-party description. Other public multilingual injection classifiers did surface:
  - Mezzo Prompt Guard v2 lists "hi" among its languages (MIT licence; snippet only; no per-language FPR checked). — [RyanStudio/Mezzo-Prompt-Guard-v2-Small](https://huggingface.co/RyanStudio/Mezzo-Prompt-Guard-v2-Small/blob/main/README.md)
  - Sentra-Guard translates non-English prompts to English before classifying (snippet only). — [Sentra-Guard, arXiv 2510.22628](https://arxiv.org/pdf/2510.22628)

### Inferences
- The Horizon-Labs model cannot serve as either a competitor claim or a baseline unless the team gets access. If it is private, it does not threaten novelty in published work.
- Mezzo Prompt Guard v2 could be an extra open baseline that claims Hindi support.

### Gaps
- The Horizon-Labs language list, Hindi coverage and per-language FPR are unknown. A logged-in HF account might show the card if the repo is gated rather than private.

## Srinivasan et al., Scientific Reports 2026 (PMC13201763) and the Kaggle dataset "hindi-and-hinglish-prompts"

### Takeaway
This is the closest direct competitor, but it differs from the planned benchmark on almost every axis:
- The data is mostly Google-Translated and machine-transliterated from English sources, despite being called "manually crafted".
- "Hinglish" here means transliterated romanized Hindi, not code-mixed text.
- There is no benign trigger-word subset, though the detector's rule layer has "override_triggers".
- The authors train their own XLM-R, DistilBERT and classical classifiers with an 80/20 split. They do not test off-the-shelf guards and give no per-register FPR or fairness metric.
- The dataset is CC0.

### Cited Findings
- Citation: Srinivasan J, Regi SA, Anbarasan AK, A S, T V, Venu S (VIT Vellore). "Detection and analysis of prompt injection in Indian multilingual large language models." *Sci Rep* 16:16208, April 2026, DOI 10.1038/s41598-026-43883-0. — [Europe PMC record (primary)](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=PMCID:PMC13201763&format=json&resultType=core); [Nature](https://www.nature.com/articles/s41598-026-43883-0); [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13201763/)
- The abstract claims "there are no publicly available datasets or any known defense mechanisms" for prompt injection in Indian regional or code-mixed languages. — [Europe PMC](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=PMCID:PMC13201763&format=json&resultType=core)
- Dataset: 4,000 prompts (2,000 Hindi and 2,000 "Hinglish"), each split 1,000 safe and 1,000 injection. Columns are Prompts, Type, Language (Hindi/Hinglish) and Translation (English). — [Full text via Europe PMC fullTextXML (primary)](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13201763/fullTextXML)
- Data provenance (from the full text):
  - It is largely machine-translated. The paper says English prompts were "first collected from existing repositories and research papers, then it was translated to Hindi and transliterated to Hinglish". It also says "Google Translator was used to from translation. An online website was used to perform transliteration."
  - Some prompts came from querying LLMs, and "some were even manually written". Human verification is claimed.
  - The source list includes deepset/prompt-injections.
  - — [Full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13201763/fullTextXML)
- The authors list the translation risk under Threats to validity: "Many of the prompts were translated and transliterated from English to Hindi and Hinglish respectively. This can bring up translation style patterns that the models may learn instead of the real attack behaviour." — [Full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13201763/fullTextXML)
- "Hinglish" in this paper is produced by transliterating English-source prompts, so it is romanized Hindi rather than natural code-mixing. The paper has no separate code-mixed register and no English parallel register as an evaluation condition. — [Full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13201763/fullTextXML)
- Models are trained and tested on the authors' own data with an 80:20 split:
  - Classical: LR, RF, SVM and XGBoost on TF-IDF.
  - Fine-tuned: XLM-RoBERTa-base and DistilBERT-multilingual.
  - A rule layer of 487 regex keywords: 103 override_triggers ("e.g., 'ignore previous instructions', 'forget earlier'"), 180 harmful_keywords and 204 benign_keywords.
  - Headline result for the hybrid model: 99.70% accuracy, P 99.65, R 99.75, F1 99.70. The only FPR figure is an aggregate ROC point, FPR 0.0035 at TPR 0.9955.
  - There is no per-language (Hindi vs Hinglish) FPR. The paper does not evaluate off-the-shelf guards (no Prompt Guard, Llama Guard, ProtectAI or similar).
  - — [Full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13201763/fullTextXML)
- On ChatGPT and Gemini, a small manual test found that "code mixed Hinglish prompts were sometimes less effectively blocked than English prompts" (qualitative only). — [Full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13201763/fullTextXML)
- The Data Availability statement reads "Data will be made available on request" and links the Kaggle dataset `sillaannregi/hindi-and-hinglish-prompts`. — [Full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13201763/fullTextXML)
- Kaggle metadata, as of 2026-10-13:
  - Title "Hindi and Hinglish Prompts", subtitle "Hindi and Hinglish Prompts for Prompt Injection Detection", owner Silla Ann Regi (a co-author).
  - **License: CC0: Public Domain**. Version 1, last updated 2025-12-10.
  - 335,842 bytes, 41 downloads, 356 views, usability 0.47.
  - Columns: prompt, language, safe/injected label, translation.
  - — [Kaggle API metadata (primary)](https://www.kaggle.com/api/v1/datasets/view/sillaannregi/hindi-and-hinglish-prompts); [Kaggle page](https://www.kaggle.com/datasets/sillaannregi/hindi-and-hinglish-prompts/data)

### Inferences
- Novelty versus Srinivasan holds on six points:
  1. Native-speaker authorship instead of Google Translate plus transliteration.
  2. Four parallel registers (English, Devanagari, romanized, code-mixed) instead of two non-parallel ones.
  3. A deliberate benign trigger-word subset (30% of benign seeds) to stress over-defense.
  4. Evaluation of off-the-shelf detectors instead of in-distribution training.
  5. Per-register FPR.
  6. Fairness metrics (FPR parity gap, FPR at matched English TPR).
- Srinivasan's own Threats-to-validity paragraph directly motivates the native-written design and can be quoted.
- The CC0 dataset could serve as a secondary external test set, with clear caveats about machine translation and transliteration artefacts. The licence allows reuse.

### Gaps
- The Kaggle CSV was not downloaded (it needs authentication), so the share of safe prompts containing trigger words like "ignore", "bhool jao" or "निर्देश" was not checked empirically. The paper does not describe a benign trigger-word subset. It treats trigger phrases only as rule-layer features.

## ACL-workshop and Findings papers 2025–2026 (CALCS, WOAH, LLMSEC, TrustNLP), IndicSafe, and 2026 Indic safety benchmarks

### Takeaway
No ACL-venue paper was found that measures guard or moderation false positives on Hindi or Hinglish. Indic safety benchmarks from 2026 (IndicSafe, IndicSafeEval) evaluate LLM behaviour in native scripts, not injection detectors, and do not cover romanized or code-mixed Hindi. Code-mixing papers measure attack success, not benign false positives.

### Cited Findings
- **IndicSafe** (Pattnayak and Chowdhuri, Oracle; arXiv 2603.17915, March 2026, v2 in May 2026):
  - 6,000 prompts, 500 per language, over 12 languages: Hindi, Bengali, Odia, Tamil, Telugu, Kannada, Malayalam, Marathi, Gujarati, Punjabi, Nepali, Urdu.
  - Written in English and translated by native speakers. Native scripts only, with no romanized or code-mixed evaluation data.
  - Evaluates 10 general LLMs via API with a GPT-4o judge. No guard classifiers, no prompt injection.
  - The closest benign-side numbers: harmless controls refused about 4–9% across languages, and qwen1.5-7B refused 33.6% of harmless Hindi prompts (top-10 table, Appendix A.10).
  - Data is at github.com/ppattnayak/indicsafe; the dataset licence is not stated.
  - — [IndicSafe HTML (primary)](https://arxiv.org/html/2603.17915)
- **IndicSafeEval** (Mondal, Mamta, Varshney, Cocarascu, Ekbal; arXiv 2609.03781, Findings of EMNLP 2026): a persuasion-based jailbreak framework with 7,200 adversarial prompts in Hindi, Bengali, Marathi and Punjabi, run against open LLMs. No benign false-positive measurement, guard evaluation or romanized/code-mixed coverage is mentioned in the abstract. — [arXiv abstract (abstract-only)](https://arxiv.org/abs/2609.03781)
- **Tongue-Tied** (CALCS 2025): a jailbreak attack using new-language learning and code-switching. It is attack-side; the languages were not confirmed from the snippet. — [ACL Anthology 2025.calcs-1.5 (snippet-only)](https://aclanthology.org/2025.calcs-1.5/)
- **Banerjee et al.**, "Attributional safety failures in LLMs under code-mixed perturbations" (arXiv 2505.14469, v2 Nov 2025): attack success rate rises from 9% in monolingual English to 69% under code-mixed inputs, and exceeds 90% for Arabic and Hindi contexts. It measures harmful-output ASR of open LLMs, not guard false positives. — [arXiv abstract (abstract-only)](https://arxiv.org/abs/2505.14469)
- **Mātṛkā** (BHASHA 2025 workshop): a multilingual jailbreak evaluation of open-source LLMs. Whether it covers Hindi or Hinglish is unknown. — snippet only, via search result listing; no direct page read.
- **HaloGuard 1.0** (Sangameswaran, Preetham S, Lenin; arXiv 2607.02079, July 2026):
  - A 46-language harm classifier that includes Hindi. Its translation prompt requires Devanagari, "never Romanized Hinglish".
  - Reports average FPR of 4.3 (0.8B) and 3.5 (4B) across its evaluations. No per-language Hindi FPR appears in the portion read.
  - Documents a failure mode in which an earlier design learned that non-Latin script alone raised the unsafe score, firing "at near-unit confidence" on benign sentences.
  - Harm only, no prompt injection.
  - — [HaloGuard HTML (primary, ~100k of 162k chars read)](https://arxiv.org/html/2607.02079)

### Inferences
- The script-as-spurious-cue failure in HaloGuard is direct published evidence that guards can over-flag benign non-Latin text. It supports the hypothesis that Devanagari benign FPR may differ from English FPR, and that romanized text may behave differently again.
- Indic safety work so far evaluates generators, not detectors, and does not cover romanized or code-mixed Hindi. The planned work fills the detector-side, register-side gap.

### Gaps
- The ACL Anthology event pages for WOAH, LLMSEC and TrustNLP 2025–2026, and the CALCS 2026 proceedings, were not browsed paper by paper. The tool-call budget only allowed searches. A targeted manual pass on "Hinglish", "code-mixed" and "romanized" in those volumes is still recommended before submission.
- The HaloGuard results sections (7.3–7.4) were not fully read. They may contain per-language FPR that includes Hindi (Devanagari only).

## 2026 papers measuring guard false positives on romanized or transliterated text in any language

### Takeaway
One 2026 paper does this for Bangla: BanglaVeilGuard (ICCA 2026). It evaluates Qwen3Guard-Gen-4B, Nemotron-SG-8B and its own guard over six Bangla forms, including romanized, Banglish and code-mixed, with prompt injection in its unsafe taxonomy. Its variants are rule-generated, its false-positive numbers are mostly over-refusal of gated LLMs rather than per-form guard FPR, it uses no fairness metric, and it does not cover Hindi. No equivalent was found for Arabizi or romanized Urdu.

### Cited Findings
- **BanglaVeilGuard** (Hassan and Hossain; arXiv 2608.21880, 25 Aug 2026; accepted at ICCA 2026):
  - Six forms: standard Bangla, romanized Bangla, Banglish, code-mixed Bangla–English, noisy, dialectal.
  - The romanized, Banglish, code-mixed and noisy variants are generated by rule-based transliteration, noun-only English substitution and spelling noise from seeds taken from XSafety, MultiJail, Multilingual-Vuln-LLMs and BIDWESH. Dialectal rows come from BIDWESH.
  - Its unsafe taxonomy explicitly includes prompt injection, prompt leaking and goal hijacking.
  - — [BanglaVeilGuard HTML (primary)](https://arxiv.org/html/2608.21880)
- BanglaVeilGuard reports per-form over-refusal only for BanglaVeilGuard-gated LLM runs. Examples:
  - Claude Opus 4.8 gated: standard 40.0%, romanized 40.0%, Banglish 33.3%, code-mixed 33.3%, dialectal 73.3%.
  - Unguarded TigerLLM-9B: 60.0% on romanized and 66.7% on Banglish.
  - Guard FPR is given only overall: BanglaVeilGuard 20.0%, Qwen3Guard-Gen-4B 13.3%, Nemotron-SG-8B 35.6%.
  - There is no FPR-gap or fairness metric. The authors warn that per-form confidence intervals are wide.
  - Hindi is not analysed.
  - — [BanglaVeilGuard HTML](https://arxiv.org/html/2608.21880)
- **PIDS-Bench** (Shire and Kim; arXiv 2609.15017, Sept 2026; IEEE Access vol. 14):
  - Evaluates prompt-injection detectors at fixed thresholds on hard-benign, obfuscated and shifted inputs.
  - A detector with F1 > 0.98 still misclassifies about one-third of an externally sourced, security-adjacent benign subset ("provenance-sensitive over-defense").
  - The abstract does not mention multilingual, transliterated or Hindi data.
  - — [arXiv abstract (abstract-only)](https://arxiv.org/abs/2609.15017)
- **Related English-only over-defense work:**
  - InjecGuard (arXiv 2410.22770), a benchmark of over-defense in injection guardrails. — [arXiv PDF (snippet-only)](https://arxiv.org/pdf/2410.22770)
  - "Passing the Test You Trained On" (arXiv 2610.03448, Oct 2026): one detector flags 0.5% of web pages but 30.1% of AgentDojo tool outputs and 66.9% of τ-bench outputs. — [arXiv HTML (snippet-only)](https://arxiv.org/html/2610.03448)
- Searches for romanized Urdu, Arabizi and transliterated prompt-injection detection with false positives (2026) returned no matching paper. — searches on 2026-10-13; no source to cite.

### Inferences
- BanglaVeilGuard is the strongest methodological precedent and must be cited as related work. The planned contribution differs in six ways:
  1. Hindi rather than Bangla.
  2. Native-speaker-written parallel registers rather than rule-generated variants.
  3. Injection-detector focus with a benign trigger-word subset.
  4. Per-register guard FPR rather than gated-LLM over-refusal.
  5. Explicit fairness metrics (FPR parity gap, FPR at matched English TPR).
  6. Larger per-register benign subsets: 200 benign seeds per register, against BanglaVeilGuard's small subsets with wide CIs.
- Taking all questions together, the novelty claim is supportable with careful wording. Defensible phrasing: "first native-speaker-written, register-parallel benchmark measuring false-positive rates and FPR fairness of prompt-injection detectors on benign Hindi in Devanagari, romanized and code-mixed forms." Avoid unqualified claims like "first Hindi prompt-injection dataset" (Srinivasan 2026 exists) or "first cross-script guard over-refusal study" (BanglaVeilGuard 2026 exists).

### Gaps
- Coverage of Arabizi, romanized Urdu and romanized Nepali guard work relies on web search only. No exhaustive arXiv listing scan was done.
- The full text of PIDS-Bench was not read to rule out a transliteration or obfuscation subset that includes romanized Hindi.
