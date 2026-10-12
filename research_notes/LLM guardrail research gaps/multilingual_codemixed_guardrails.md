# Multilingual, Low-Resource and Code-Mixed (Hindi / Hinglish / Indic) Evaluation of LLM Guardrails, with False Positives as a Fairness Issue

Scope note: research done 2026-10-12 with web search and fetch. "Verified" means I fetched the primary page (arXiv abstract or HTML, PMC full text, or the HF model card) or got a direct search snippet from it. Items I know from background but did not re-check this session are marked **[not re-verified]** or listed under Gaps. The team's own numbers (40% FPR on benign Hindi and Hinglish, about 0% on English) are their data. I make no claims about them.

## Q1. Multilingual guard benchmarks and models: what exists (PolyGuard, Llama Guard multilingual evals, RTP-LX, XSafety, MultiJail, Yong et al., M-ALERT, LinguaSafe, Indic benchmarks, code-mixed jailbreaks, Prompt Guard 2, Qwen3Guard)

### Takeaway
There is a lot of multilingual safety work, and Hindi shows up often (PolyGuardMix, RTP-LX, XSafety, IndicSafe, Prompt Guard 2's multilingual eval, the code-mixed jailbreak CMP-RT). Almost all of it is (a) harmful-content moderation, not prompt-injection detection, (b) attack-side, measuring how far ASR or unsafe output rises in non-English, and (c) built from translated text, not natively written or romanized/code-mixed text. The only Hindi + Hinglish prompt-injection dataset I found is one small 2026 Scientific Reports paper. Its data is machine-translated or transliterated, and it reports no per-language over-defense analysis and no off-the-shelf detector baselines.

### Cited Findings
**Harmful-content guard models and benchmarks**
- PolyGuard (COLM 2025, CMU and collaborators) is a multilingual safety moderation model for 17 languages, Hindi among them. It is trained on PolyGuardMix (1.91M samples: in-the-wild multilingual human-LLM chats plus machine translations of English WildGuardMix) and evaluated on PolyGuardPrompts (29K samples with prompt-harm, response-harm and refusal labels). Translation quality and safety labels were human-checked across the 16 non-English languages. Reported gains over prior classifiers differ between versions (5.5% vs 4.1%). — [PolyGuard arXiv 2504.04377](https://arxiv.org/abs/2504.04377v1); [HF model ToxicityPrompts/PolyGuard-Qwen](https://huggingface.co/ToxicityPrompts/PolyGuard-Qwen); [PolyGuardMix dataset](https://huggingface.co/datasets/ToxicityPrompts/PolyGuardMix/commit/645d9f4d914c53e4b2afb9d61e3c53bdb742091c)
- Qwen3Guard (Oct 2025) comes in generative and streaming variants, 0.6B/4B/8B, supports "up to 119 languages and dialects", and is Apache-2.0. A secondary summary says training content was translated into 15 additional languages with Qwen-MT. — [Qwen3Guard Technical Report arXiv 2510.14276](https://arxiv.org/abs/2510.14276v1); translation detail only from [Moonlight review](https://www.themoonlight.io/fr/review/qwen3guard-technical-report) (secondary, not checked against the PDF)
- Yang, Dan, Roth & Lee, "Benchmarking LLM Guardrails in Handling Multilingual Toxicity" (arXiv 2410.22153, Oct 2024) evaluated Llama-Guard-2/3, Aegis-Defensive and MD-Judge on 7 datasets (ToxicChat, Aegis, OpenAI Moderation, RTP-LX, PTP, MultiJail, XSafety). The English sets were Google-translated into ZH, DE, RU, AR, KO, ID, BN, SW. A code-switched MultiJail variant (CSRT-style, generated with gpt-3.5-turbo) was included. On MultiJail F1, MD-Judge fell from 92.31 (EN) to 37.05 (non-EN) and 49.64 (code-switched), and Llama-Guard-3 from 80.23 to 76.70 / 75.25. Hindi is present only inside RTP-LX/XSafety and is not analysed on its own. — [arXiv 2410.22153](https://arxiv.org/html/2410.22153v1)
- RTP-LX (AAAI 2025) is a human-transcreated, human-annotated corpus of toxic prompts and outputs in 28 languages, derived from RealToxicityPrompts. It found that LLM evaluators score acceptable accuracy but agree poorly with humans on holistic toxicity, and they miss microaggressions and identity attacks. — [RTP-LX arXiv 2404.14397](https://arxiv.org/abs/2404.14397v2); [AAAI](https://ojs.aaai.org/index.php/AAAI/article/view/35011)
- XSafety ("All Languages Matter", ACL Findings 2024) covers 14 safety issues in 10 languages. All four tested LLMs gave significantly more unsafe responses to non-English queries. — [arXiv 2310.00905](https://arxiv.org/abs/2310.00905v2)
- MultiJail (Deng et al., ICLR 2024): English harmful queries translated by native speakers into 9 languages. Low-resource languages show about 3x the rate of harmful content for ChatGPT and GPT-4. — [arXiv 2310.06474](https://arxiv.org/abs/2310.06474v3)
- Yong, Menghini & Bach, "Low-Resource Languages Jailbreak GPT-4" (NeurIPS 2023 SoLaR workshop): translating unsafe prompts into low-resource languages raised GPT-4 bypass from <1% to 79%. — [arXiv 2310.02446](https://arxiv.org/pdf/2310.02446)
- M-ALERT ("LLMs Lost in Translation"): 75k prompts (15k per language) in EN/FR/DE/IT/ES, with category-level cross-lingual inconsistencies. No Indic languages. — [arXiv 2412.15035](https://arxiv.org/abs/2412.15035)
- LinguaSafe: 45k entries in 12 languages (Hungarian to Malay), built from translated, transcreated and natively sourced data. It includes an **oversensitivity** evaluation, though that is for LLMs, not guard classifiers. — [arXiv 2508.12733](https://arxiv.org/html/2508.12733v2)
- MrGuard (EMNLP 2025) is a multilingual reasoning guardrail. It is evaluated with code-switched prompts (English + one other language) on MultiJail/XSafety and treats Hindi as low-resource. — [ACL Anthology 2025.emnlp-main.1392](https://aclanthology.org/2025.emnlp-main.1392.pdf); [arXiv 2504.15241](https://arxiv.org/pdf/2504.15241)
- HaloGuard 1.0 (2026) is an open-weights multilingual constitutional classifier. It reports an overall FPR of 4.3 across seven English-centric prompt-safety benchmarks, and the retrieved text gives no per-language FPR. — [arXiv 2607.02079](https://arxiv.org/html/2607.02079)

**Indic-specific safety benchmarks (LLM-response focused)**
- IndicSafe (Pattnayak & Chowdhuri, Oracle; arXiv 2603.17915, 2026) has 6,000 prompts (500 x 12 Indic languages incl. Hindi, Urdu, Bengali, Marathi, Nepali). Prompts were authored in English, translated by native speakers and spot-checked by bilingual reviewers (720 reviewed, 28 replaced), and issued in **native scripts**, with no romanized or code-mixed variant. It evaluates **10 generative LLMs** judged by GPT-4o and **no dedicated guard classifiers**. It reports over-refusal of harmless prompts, e.g. Mistral-7B refusing 61.6% of Punjabi harmless prompts and Qwen1.5-7B refusing 33.6% of Hindi harmless prompts. The "Category Bias Score" has no formula given. Licence CC BY-NC 4.0. — [arXiv 2603.17915v2](https://arxiv.org/html/2603.17915v2); [GitHub](https://github.com/ppattnayak/indicsafe)
- IndicSafeEval (arXiv 2609.03781, 2026): 7,200 adversarial persuasive-jailbreak prompts translated into Hindi, Bengali, Marathi and Punjabi. Hindi showed the highest average vulnerability. Attack side only. — [arXiv 2609.03781](https://arxiv.org/html/2609.03781v1)
- SurakshaEval (arXiv 2608.07862, 2026): human-written prompts for 10 Indian languages + English. A reviewer flags that its "safety gap" metric equates safety with government approval. — [Pith review](https://pith.science/paper/2608.07862); [listing](https://awesomepapers.io/llm-papers/papers/2608.07862) (I did not fetch the primary arXiv page)
- PARIKSHA ran a preliminary safety check with Hindi RTP-LX prompts, using an LLM evaluator only. — [arXiv 2406.15053](https://arxiv.org/pdf/2406.15053)

**Code-mixed / code-switching jailbreaks**
- CSRT, "Code-Switching Red-Teaming" (Yoo, Yang & Lee; ACL 2025): code-switched queries mixing up to 10 languages produced 46.7% more successful attacks than English. Ablations link resource level to safety alignment. The abstract does not mention Hindi and does not measure benign over-refusal. — [arXiv 2406.15481](https://arxiv.org/abs/2406.15481)
- "haet bhasha aur diskrimineshun" / CMP-RT (Aswal & Jaiswal; arXiv 2505.14226, v5 Apr 2026): phonetic perturbations in romanized Hinglish (e.g. "DDoS" becomes "dee dee o es") jailbreak SOTA models including Gemini-3-Pro. The authors attribute this to **tokenization**: perturbations split safety-critical tokens into benign sub-words and lower their attribution. This is attack-side. The abstract does not say whether guard classifiers were tested. — [arXiv 2505.14226](https://arxiv.org/abs/2505.14226)

**Prompt-injection detectors with multilingual claims**
- Llama Prompt Guard 2 86M (Meta) uses an mDeBERTa base and is "trained to detect both English and non-English injections and jailbreaks". Its multilingual eval covers EN, FR, DE, **Hindi**, IT, PT, ES and TH, but it reports only an aggregate AUC (0.995 for 86M, 0.942 for 22M), with **no per-language breakdown and no multilingual FPR**. Recall@1%FPR is English only. The 22M model uses English deberta-v3-xsmall and has a larger multilingual gap. The tokenizer was modified against fragmentation and whitespace attacks, with no details given. — [HF model card](https://huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M)
- Horizon-Labs/prompt-injection-guard-multilingual (HF) reportedly gives per-language FPRs on **machine-translated** benign data (e.g. about 0.46 RU and about 0.67 ZH at threshold 0.5). It warns that the benign halves contain "failed attacks", so the multilingual FPR is an upper bound, and that its XSTest FPR is English-only. — search-snippet summary of the [HF card](https://huggingface.co/Horizon-Labs/prompt-injection-guard-multilingual). A direct fetch returned HTTP 401, so these numbers are **not directly verified**.
- Sentra-Guard (arXiv 2510.22628) reports Hindi and Arabic detection above 94% vs 99.5% English and credits a translation-normalization layer. Snippet only. — [arXiv 2510.22628](https://arxiv.org/pdf/2510.22628)
- MIPIAD (arXiv 2605.07269): multilingual indirect prompt-injection defense (Qwen + TF-IDF hybrid). It warns that even a 1% FPR flags most legitimate queries at realistic attack base rates. Snippet only. Language list not verified. — [arXiv 2605.07269](https://arxiv.org/pdf/2605.07269)

**Closest direct competitor (Hindi + Hinglish prompt injection)**
- Srinivasan et al. (VIT), "Detection and analysis of prompt injection in Indian multilingual large language models", *Scientific Reports* 16:16208 (published 2026-04-04):
  - Data: 4,000 prompts, of which 2,000 are Hindi and 2,000 Hinglish (romanized), each split 1,000 safe / 1,000 injection. English prompts came from Kaggle, HF, LLM queries and manual writing. They were **Google-Translated** to Hindi and **transliterated with an online tool** to Hinglish. "Human verification was done."
  - Availability: data "available on request", plus a Kaggle dataset "hindi-and-hinglish-prompts".
  - Models: TF-IDF + LR/RF/SVM/XGBoost, XLM-R-base, DistilBERT-multilingual, and an XLM-R + regex hybrid. Testing used an in-distribution 80/20 split with **no cross-dataset eval**.
  - Reporting: **no headline benign FPR and no per-language FPR.** The full-dataset confusion matrix (train+test) implies about 0.45% safe-as-injection. Reported accuracy (0.997) does not exactly match the confusion-matrix counts.
  - **No comparison to Prompt Guard, ProtectAI DeBERTa or other off-the-shelf detectors.**
  - It claims no public datasets or defenses exist for Indic or code-mixed prompt injection.
  - Sources: [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC13201763/); [Nature](https://www.nature.com/articles/s41598-026-43883-0)
- A GitHub project, "multilingual-llm-safety-benchmark" (EN/Hindi/Marathi), measures prompt-injection resilience of LLM **responses**, not detector FPR. — [GitHub ShriyaP1966](https://github.com/ShriyaP1966/multilingual-llm-safety-benchmark)
- A practitioner blog post (dev.to, 2026) found an agent framework's injection scanner caught 1/13 translated attack phrases and 7/42 multi-language attacks (all 7 in English). It did not test Hindi or measure benign FPR, and it names benign FPR as an open question. — [dev.to](https://dev.to/nova-agent/a-prompt-injection-detector-that-only-speaks-english-2a5h)

### Inferences
- The multilingual safety literature mostly treats non-English as an *attack vector* (under-blocking). The team's finding points the other way: non-English and code-mixed text as a *trigger for over-blocking*. This direction is much less studied, especially for prompt-injection classifiers.
- Given CMP-RT's tokenization explanation for under-blocking, the same mechanism, fragmented sub-words in romanized or Devanagari text, plausibly also produces spurious high-injection scores (over-blocking). This is a hypothesis the team could test. I found no paper that tests it for PI detectors.
- The Scientific Reports paper is the closest prior work but differs in four ways: it uses machine-translated or transliterated text, not natively written text; it evaluates in-distribution only; it has no off-the-shelf baselines; and it frames the problem as detection accuracy, not language-driven over-defense or fairness. A native-speaker, human-written, three-register (Devanagari / romanized / code-mixed) benign + adversarial set used to *audit* existing PI guards (Prompt Guard 2, ProtectAI, PIGuard, etc.) would still be distinct from it.

### Gaps
- Aya red-teaming (Cohere "Multilingual Alignment Prism", which I believe includes Hindi) was not re-verified this session **[not re-verified]**. I also did not verify Llama Guard 3's official per-language results (its model card lists 8 languages incl. Hindi **[not re-verified]**).
- I could not fetch the Horizon-Labs model card (HTTP 401). Its per-language FPRs are snippet-level only.
- I did not verify whether the Sci. Rep. Kaggle dataset is actually downloadable, how large it is, or under what licence.
- I did not verify whether PolyGuard or Qwen3Guard report per-language **false positive rates** (as opposed to F1). Their papers would need to be read in full.

## Q2. Does anyone measure FALSE POSITIVES / over-refusal on benign non-English or code-mixed text for guard classifiers, especially prompt-injection detectors?

### Takeaway
Only partly. Over-defense of **prompt-injection guards** is well established, but in **English only** (NotInject/PIGuard). Over-refusal on benign non-English prompts is measured for **generative LLMs** (IndicSafe, LinguaSafe, TukaBench). For **harmful-content guards**, one paper notes high FPR on low-resource languages (Aegis-Defensive, arXiv 2410.22153), shown in a figure without Hindi or a code-mixed breakdown. I found **no peer-reviewed work reporting per-language benign FPR of prompt-injection detectors on Hindi, romanized Hindi or Hinglish**, and none framing it as fairness.

### Cited Findings
- **NotInject / InjecGuard → PIGuard (ACL 2025)** (Li, Liu, Zhang & Xiao):
  - The data is 339 benign samples enriched with injection "trigger words" (e.g. "ignore", "cancel"), at three difficulty levels and **English only**.
  - SOTA PI guards drop to near-random (about 60%) accuracy on it.
  - The MOF training strategy reduces trigger-word bias, and PIGuard beats the best prior model by 30.4% (30.8% in the arXiv version).
  - Sources: [ACL Anthology 2025.acl-long.1468](https://aclanthology.org/2025.acl-long.1468); [arXiv 2410.22770](https://arxiv.org/html/2410.22770v3); [HF leolee99/PIGuard](https://huggingface.co/leolee99/PIGuard)
- Yang et al. 2024: Aegis-Defensive shows "a high False Positive Rate (FPR) on low-resource languages", over-flagging non-English prompts as unsafe. Values appear only in Fig. 3 (Aegis dataset) and the data is machine-translated, with no Hindi-specific FPR. — [arXiv 2410.22153](https://arxiv.org/html/2410.22153v1)
- IndicSafe measures over-refusal of harmless prompts in 12 Indic languages for generative LLMs (e.g. Qwen1.5-7B 33.6% on Hindi harmless), not for guards. — [arXiv 2603.17915v2](https://arxiv.org/html/2603.17915v2)
- LinguaSafe includes "oversensitivity" evaluation across 12 languages (LLMs). — [arXiv 2508.12733](https://arxiv.org/html/2508.12733v2)
- TukaBench (2026) has a benign split (Afri-JBB-Benign) in EN + 6 African languages. Models refuse a large fraction of benign prompts (often near 50%), and the authors argue safety mechanisms over-attend to surface unsafe words (generative LLMs). — [arXiv 2606.01322](https://arxiv.org/pdf/2606.01322)
- SomaliBench Eval acknowledges that refusal needs benign controls. Its benign Somali control is listed as future work. — [arXiv 2605.25420](https://arxiv.org/html/2605.25420)
- Prompt Guard 2 publishes no per-language FPR, only aggregate multilingual AUC. — [HF card](https://huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M)
- pi-detector-bench measures PI detector false positives on **real traffic** (WildChat + LMSYS). No Hindi or Hinglish split was visible. — [GitHub bastion-soft/pi-detector-bench](https://github.com/bastion-soft/pi-detector-bench)
- The Sci. Rep. Hindi/Hinglish PI paper reports no per-language benign FPR. — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13201763/)

### Inferences
- The specific combination is, as far as I can find, unoccupied: PI detector × benign native Hindi / romanized / code-mixed × per-language FPR × fairness framing. The nearest neighbours each cover two of those four axes:
  - NotInject: PI + benign FPR, English only.
  - Yang et al.: guard + non-English FPR, harmful-content moderation, translated text.
  - IndicSafe: Indic + over-refusal, generative LLMs, native script only.
  - Sci. Rep.: PI + Hindi/Hinglish, no FPR or fairness analysis, machine-translated data.
- A natural design would be "NotInject for Hindi": benign prompts containing Hindi and Hinglish equivalents of trigger words (e.g. "ignore karo", "pichhle instructions bhool jao" used benignly). Pair them with plain benign controls to separate *script/language-driven* FP from *trigger-word-driven* FP. That distinction would be a novel analytical contribution.

### Gaps
- I could not see the per-language values in Yang et al.'s Fig. 3.
- I did not check whether PolyGuardPrompts or Qwen3Guard eval tables include a per-language "safe-labelled" FPR breakdown. If they do, a moderation-side (non-PI) Hindi FPR may exist.
- I did not search exhaustively for workshop papers (WOAH 2025/2026, CALCS 2025/2026, LLMSEC 2025) that might contain a small Hinglish guard FPR study. This is a residual novelty risk.

## Q3. Hindi / Hinglish NLP resources for building the benchmark, and known tokenization issues (DeBERTa / XLM-R / mDeBERTa)

### Takeaway
Plenty of code-mixed corpora exist for sourcing natural benign Hinglish (L3Cube-HingCorpus, HinGE, LinCE, GLUECoS). Tokenization disparity across languages and scripts is well documented (Petrov et al., NeurIPS 2023). The CMP-RT paper links Hinglish tokenization fragmentation directly to safety failures. One concrete issue: Prompt Guard 2's 22M variant uses an English-only DeBERTa, which Meta says widens its multilingual gap.

### Cited Findings
- L3Cube-HingCorpus: 52.93M sentences / 1.04B tokens of real romanized Hindi-English tweets, plus the HingLID language-ID dataset and HingBERT models evaluated on GLUECoS tasks. — [arXiv 2204.08398](https://arxiv.org/pdf/2204.08398); [WILDRE 2022](https://aclanthology.org/2022.wildre-1.2.pdf)
- HinGE: parallel Hindi-English sentences with human-written and rule-generated Hinglish, for generation and evaluation. — [arXiv 2107.03760](https://ar5iv.arxiv.org/html/2107.03760)
- LinCE (LREC 2020): centralized code-switching benchmark with Hindi-English among 4 pairs. Tasks: LID, NER, POS, sentiment. — [ACL Anthology 2020.lrec-1.223](https://aclanthology.org/2020.lrec-1.223); [arXiv 2005.04322](https://arxiv.org/pdf/2005.04322)
- GLUECoS (ACL 2020, Microsoft Research): English-Hindi and English-Spanish. Tasks: LID, POS, NER, sentiment, QA, NLI. English-Hindi results were weaker, attributed partly to Hindi's non-standardized romanization and word-order differences. — [ACL Anthology 2020.acl-main.329](https://aclanthology.org/2020.acl-main.329)
- A gold-standard code-mixed set covers English-{Hindi, Bengali, French, Spanish}, with 370 Hindi sentences. — [arXiv 2410.10580](https://arxiv.org/pdf/2410.10580)
- Hinglish has heavy spelling variation (e.g. "acha / acchha / achha"). Phonetic perturbations were already shown to break code-mixed BERT classifiers. AdvCodeMix attacks code-mixed classifiers via sub-word perturbation and language switching. — [arXiv 2310.18155](https://arxiv.org/pdf/2310.18155); [AdvCodeMix arXiv 2111.00350](https://arxiv.org/pdf/2111.00350)
- Petrov et al., "Language Model Tokenizers Introduce Unfairness Between Languages" (NeurIPS 2023): the same content can differ by up to 15x in token length across languages. Disparities persist across 17 tokenizers, including multilingual ones, and are over 4x even for byte/char-level models. Measured on FLORES-200, with code and tables available. — [NeurIPS proceedings](https://proceedings.neurips.cc/paper_files/paper/2023/hash/74bb24dca8334adce292883b4b651eda-Abstract.html); [GitHub](https://github.com/AleksandarPetrov/tokenization-fairness)
- Non-Latin scripts such as Hindi/Devanagari are multi-byte in UTF-8 and more prone to fragmentation under byte-fallback. — [arXiv 2509.20045](https://arxiv.org/pdf/2509.20045)
- CMP-RT ties Hinglish safety failures to tokenization: perturbed safety-critical words split into benign sub-words. — [arXiv 2505.14226](https://arxiv.org/abs/2505.14226)
- Prompt Guard 2: the 86M model uses an mDeBERTa base. The 22M model uses deberta-v3-xsmall, because "no multilingual-pretrained DeBERTa-xsmall exists", and has a larger multilingual gap. — [HF card](https://huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M)

### Inferences
- An English-only DeBERTa-v3 tokenizer (as in ProtectAI deberta-v3-base-prompt-injection and PIGuard's DeBERTa-v3) will badly fragment Devanagari and treat romanized Hindi as unusual English sub-words. Out-of-distribution, high-entropy token sequences are a plausible cause of the team's roughly 40% FPR. The team can measure this directly by reporting token fertility per register alongside FPR and checking correlation.
- Because romanized Hindi lacks a standard spelling, the benchmark should include controlled spelling variants of the same benign prompt to separate a "spelling-variance FP" from a "language FP".

### Gaps
- I did not verify AI4Bharat resources (IndicCorp, Aksharantar transliteration, IndicXlit, Dakshina, IndicTrans2) in this session. All are relevant for script conversion and native data. **[not re-verified]**
- I did not find published fertility numbers for XLM-R or mDeBERTa on Devanagari vs romanized Hindi. These would need to be computed.

## Q4. Fairness framing precedent: guardrail or moderation false positives on dialects or non-English text treated as bias

### Takeaway
The precedent is strong for toxicity and hate-speech classifiers: dialect-driven FPR is classic algorithmic bias (Sap et al. 2019 on AAE). Policy literature (CDT 2023) frames multilingual moderation failures, including false alarms, as harms to non-English speakers. Extending this "false positives as disparate impact" framing to *prompt-injection guards* and *code-mixed Indic text* appears new.

### Cited Findings
- Sap et al. (ACL 2019), "The Risk of Racial Bias in Hate Speech Detection": AAE markers correlate with toxicity labels, models replicate this bias, and Perspective API scores benign AAE phrases as more toxic. Dialect-aware priming reduces annotator bias. — [ACL P19-1163](https://preview.aclanthology.org/fix_video/P19-1163.pdf); [NSF PAR](https://par.nsf.gov/biblio/10107991)
- Xia, Field & Tsvetkov (2020): adversarial training substantially reduced FPR on AAE with minimal loss in hate-speech performance. Zhou et al. (EACL 2021): debiasing is limited, and relabeling data works better. — via [NSF PAR / UW](https://digital.lib.washington.edu/researchworks/bitstreams/622b386a-881b-4c31-b017-31c3a6e33de2/download) and [Demoting Racial Bias arXiv 2005.12246](https://fugumt.com/fugumt/paper_check/2005.12246v1_enmode) (secondary mirrors; not fetched in full)
- A more recent study found classifiers trained on **LLM-generated labels** (GPT-4, Llama-3) still show higher FPR on AAE than SAE tweets. — [NSF PAR 10612700](https://par.nsf.gov/biblio/10612700-large-language-model-annotation-bias-hate-speech-detection)
- CDT, "Lost in Translation: Large Language Models in Non-English Content Analysis" (May 2023):
  - Multilingual models are trained disproportionately on English and transfer English assumptions to other languages.
  - They perform worse in lower-resource languages, and MT compounds errors.
  - Recommendations: narrow remits and human review.
  - Sources: [CDT report PDF](https://cdt.org/wp-content/uploads/2023/05/Lost-in-Translation-es-english-final-05172023.pdf); [CDT primer](https://cdt.org/wp-content/uploads/2023/05/non-en-content-analysis-primer-051223-1203.pdf)
- Rest of World (2023) reports that English-trained hate-speech notions transferred to other languages cause "more errors and false alarms". CDT's follow-up on Tamil moderation notes that inaccurate moderation led to loss of trust and suppression of speech. — [Rest of World](https://restofworld.org/2023/ai-content-moderation-hate-speech/); [Tech Policy Press](https://techpolicy.press/lost-in-translation-how-content-moderation-fails-tamil-speakers-online)
- Petrov et al. explicitly frame tokenization disparity as "unfair treatment" of language communities (cost, latency, context). — [NeurIPS 2023](https://proceedings.neurips.cc/paper_files/paper/2023/hash/74bb24dca8334adce292883b4b651eda-Abstract.html)
- IndicSafe frames cross-language safety drift and "refusal bias" as an equity issue for South Asian users. — [arXiv 2603.17915v2](https://arxiv.org/html/2603.17915v2)

### Inferences
- The team can borrow standard fairness metrics: per-group FPR gaps (equalized odds / FPR parity), disparate impact ratios, and FPR at a matched English TPR operating point. They can then frame a 40% vs ~0% gap as a **quality-of-service harm**: Hindi/Hinglish users of a guarded LLM app are blocked about 40x more often for benign requests. This mirrors the AAE precedent directly.
- MIPIAD's base-rate point makes the harm concrete: in deployment, benign traffic dominates, so per-language FPR determines who gets blocked.

### Gaps
- I did not find a paper that applies formal fairness metrics to *prompt-injection* or *jailbreak* classifiers across languages or dialects. This absence is itself the gap. A targeted search of FAccT/AIES 2024–2026 was not done.

## Q5. What remains open: concrete gaps and closest competitors

### Takeaway
The planned contribution looks novel on the intersection of four things:
- (i) prompt-injection / jailbreak *detector* evaluation, not LLM responses or harmful-content moderation;
- (ii) *benign false positives* as the primary metric, framed as fairness;
- (iii) *three Hindi registers* (Devanagari, romanized, code-mixed) that are **natively written and human-validated** rather than machine-translated;
- (iv) cross-model auditing of existing open guards.

The closest competitors are Srinivasan et al. 2026 (Sci. Rep.), NotInject/PIGuard (ACL 2025), Yang et al. 2024 and IndicSafe 2026. Each covers only part of this.

### Cited Findings (closest competitors and what each lacks)
- **Srinivasan et al. 2026, Sci. Rep.**
  - Overlap: Hindi + romanized Hinglish PI dataset (4k, balanced).
  - Missing: data is machine-translated and transliterated; in-distribution eval only; no benign FPR or per-language analysis; no external guard baselines; no fairness framing; no Devanagari-vs-roman-vs-code-mixed comparison of the *same* content.
  - Source: [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13201763/)
- **NotInject / PIGuard (ACL 2025)**
  - Overlap: defines and benchmarks PI over-defense.
  - Missing: English only.
  - Source: [ACL](https://aclanthology.org/2025.acl-long.1468)
- **Yang et al. 2024**
  - Overlap: guard FPR higher on low-resource languages, plus code-switching.
  - Missing: harmful-content guards only; Google-translated data; no Hindi analysis; FPR only in a figure.
  - Source: [arXiv 2410.22153](https://arxiv.org/html/2410.22153v1)
- **IndicSafe 2026**
  - Overlap: 12 Indic languages, human-translated, measures over-refusal.
  - Missing: generative LLMs only; native script only; no code-mixed or romanized text; no PI.
  - Source: [arXiv 2603.17915v2](https://arxiv.org/html/2603.17915v2)
- **CMP-RT (Aswal & Jaiswal)**
  - Overlap: romanized Hinglish, with a tokenization mechanism.
  - Missing: attack side only; no benign FPR.
  - Source: [arXiv 2505.14226](https://arxiv.org/abs/2505.14226)
- **Prompt Guard 2**
  - Overlap: claims Hindi in its multilingual eval.
  - Missing: no per-language FPR published, which leaves an open, checkable claim.
  - Source: [HF card](https://huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M)
- **PolyGuard, Qwen3Guard**
  - Overlap: multilingual moderators that include Hindi.
  - Missing: harmful-content moderators, not PI; romanized and code-mixed coverage not documented in the sources I checked.
  - Sources: [PolyGuard](https://arxiv.org/abs/2504.04377v1); [Qwen3Guard](https://arxiv.org/abs/2510.14276v1)

### Inferences (open problems the team could claim)
1. **No human-written, native-speaker benign benchmark exists for PI detectors in Devanagari, romanized Hindi and Hinglish, with per-register FPR.** This is the core gap. Machine translation is the norm in competitors (Yang et al., Sci. Rep.) and has documented quality caveats (CDT).
2. **No public per-language FPR audit of off-the-shelf PI guards** (Prompt Guard 2 86M/22M, ProtectAI deberta-v3, PIGuard, Qwen3Guard used as PI filter) on Hindi or Hinglish. This audit is cheap to run and immediately useful.
3. **No disentangling of FP causes**: script (Devanagari vs Latin), language, code-mixing ratio, spelling variance, and trigger-word translations. A NotInject-style Hindi/Hinglish trigger-word split would extend PIGuard's methodology cross-lingually.
4. **No linkage between tokenizer fertility and FPR for guards.** CMP-RT shows fragmentation drives under-blocking. The reverse (over-blocking) is untested.
5. **No fairness-metric framing** (FPR parity, disparate impact) for PI guards across languages. AAE toxicity work gives direct precedent.
6. **Mitigation**: whether MOF-style training (PIGuard), translation-normalization (Sentra-Guard), or adding natively written Hinglish benign data closes the gap without lowering attack recall. Report this at matched TPR.

### Gaps
- Novelty risk remains from (a) workshop papers or preprints in late 2026 that I did not find, (b) the Horizon-Labs card if it adds Hindi, and (c) unread full texts of PolyGuard/Qwen3Guard, which may contain per-language FPR tables. I recommend a targeted check of arXiv listings for "Hinglish" + "prompt injection" and of CALCS/WOAH 2026 proceedings before submission.
- The Sci. Rep. Kaggle dataset should be downloaded and inspected. If it is usable, it is both a baseline and a contrast: machine-translated vs native text.
