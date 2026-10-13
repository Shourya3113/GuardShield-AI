# Follow-up: Uysal et al. 2026 and Handa et al. 2025 (cited in arXiv 2609.26176) and whether they pre-empt Paper 1

Scope: two references cited in "Refusing Everything Looks Safe" (arXiv 2609.26176), checked against Paper 1 claims (1) paired benign-twin perturbation protocol for prompt-injection detectors, (2) score-level paired metrics, (3) cross-guard fail-closed vs fail-open audit per perturbation family, (4) Hindi / romanized Hindi / Hinglish over-defense benchmark with fairness metrics, (5) script-aware canonicalization vs benign-twin augmentation, on seen vs held-out families. Date of check: 2026-10-13.

Reading status: the arXiv HTML full text was fetched for both papers (Uysal v1, Handa v5) and for 2609.26176. The Handa over-defense figure (Fig. 5) gives only one exact number in the text. Other numbers come from the prose. An extra paper, PIDS-Bench (arXiv 2609.15017), turned up during the search and is the closest prior work found. Its HTML was read only to about the first 100k of 186k characters, so its appendices were not checked.

## Q1. What is "Uysal et al. 2026", and does it evaluate detectors or guards, Hindi or code-mixed text, obfuscations, benign false positives, or mitigations?

### Takeaway
Uysal et al. is arXiv 2606.29602, a jailbreak-style compliance study of six frontier chat LLMs. It covers English, Turkish, Russian and Simplified Chinese, plus Base64, ROT13 and Hex encodings. It evaluates no detector or guard and has no benign controls or false-positive measurement. It has no Hindi, romanized or code-mixed text and tests no mitigation. It does not pre-empt any of claims (1) to (5).

### Cited Findings
- **Bibliography entry in 2609.26176:** Uysal, C.; Birinci, B.; Mutluergil, S. O.; Çetin, O. (2026), "An Empirical Evaluation of Prompt Injection Vulnerabilities Across Multilingual and Obfuscated Attack Scenarios," arXiv preprint. The entry gives no ID. — [arXiv 2609.26176 HTML](https://arxiv.org/html/2609.26176)
- **How 2609.26176 uses it:** Uysal is cited once, in Related Work, alongside Prakash et al. 2026, for "multilingual or cross-model obfuscation". — [arXiv 2609.26176 HTML](https://arxiv.org/html/2609.26176)
- **Exact paper:** arXiv **2606.29602**, "An Empirical Evaluation of Prompt Injection Vulnerabilities in Large Language Models Across Multilingual and Obfuscated Attack Scenarios" (the full title adds "in Large Language Models"). Authors: Çağlar Uysal, Baturay Birinci, Süha Orhun Mutluergil, Orçun Çetin (Sabancı University). Submitted 28 June 2026, cs.CR. — [arXiv abs 2606.29602](https://arxiv.org/abs/2606.29602)
- **Venue:** accepted to the AI-SS 2026 Workshop at the 21st European Dependable Computing Conference (EDCC 2026), EDCC Companion Proceedings. This comes from search snippets of the abstract page. — [arXiv abs 2606.29602](https://arxiv.org/abs/2606.29602)
- **Models:** DeepSeek-V3.2, Gemini 2.5 Flash, GPT-5 Mini, Grok-4-1-Fast (Non-Reasoning), Llama 4 Scout Instruct, and Qwen 3 235B A22B Instruct. Open models ran via Replicate with default safety settings. — [arXiv HTML 2606.29602v1](https://arxiv.org/html/2606.29602v1)
- **Languages:** English, Turkish, Russian, Simplified Chinese, translated with DeepL. There is **no Hindi, no romanized and no code-mixed** text. — [arXiv HTML 2606.29602v1](https://arxiv.org/html/2606.29602v1)
- **Obfuscations:** Base64, ROT13 and Hex only. Only the malicious-behaviour span is encoded, and the surrounding instruction stays in English. — [arXiv HTML 2606.29602v1](https://arxiv.org/html/2606.29602v1)
- **Data:**
  - 37 prompt templates from the authors' prior work: phishing email (7 direct, 6 elaborate), phishing webpage (7 direct, 6 elaborate) and keylogger (6 direct, 5 elaborate).
  - "Elaborate" prompts wrap the request in security-training or red-team framing.
  - Each template × condition × model ran 10 times, giving 15,540 outputs (2,590 per model; 2,220 per language or encoding).
  - The abstract says "multi-stage obfuscated attacks", but the method section never defines a multi-stage procedure.
  - [arXiv HTML 2606.29602v1](https://arxiv.org/html/2606.29602v1)
- **Metric:** a single human expert labels each response as full compliance, stalling or refusal, plus a warning flag. "Fulfillment" means compliance plus stalling. No inter-annotator agreement is reported. — [arXiv HTML 2606.29602v1](https://arxiv.org/html/2606.29602v1)
- **Key numbers:** all from [arXiv HTML 2606.29602v1](https://arxiv.org/html/2606.29602v1).

  | Breakdown | Full compliance |
  |---|---|
  | Overall | 68.76% (stalling 12.08%, refusal 19.16%, fulfillment 80.84%) |
  | DeepSeek | 84.32% |
  | Gemini | 77.72% |
  | Grok | 72.55% |
  | Qwen | 67.84% |
  | Llama | 66.02% |
  | GPT-5 Mini | 44.09% |
  | Turkish | 80.18% |
  | Simplified Chinese | 77.52% |
  | Russian | 73.92% |
  | English | 71.31% |
  | Base64 | 65.59% |
  | ROT13 | 58.38% |
  | Hex | 54.41% |

- **No detectors or guards:** the paper does not evaluate Llama Guard, Prompt Guard, Lakera or any other classifier. — [arXiv HTML 2606.29602v1](https://arxiv.org/html/2606.29602v1)
- **No benign side and no mitigation:** there are no benign control prompts, no false-positive or over-refusal measurement, and no mitigation is tested. The discussion only suggests multilingual coverage, intent detection and encoding-aware handling as future directions. — [arXiv HTML 2606.29602v1](https://arxiv.org/html/2606.29602v1)
- **Threat model:** despite the "prompt injection" framing, Sec. III-A is direct malicious requests to the model. It is not indirect or application-level injection. — [arXiv HTML 2606.29602v1](https://arxiv.org/html/2606.29602v1)

### Inferences
- **Overlap with Paper 1: none on any claim.** Uysal is an attack-success study of generator LLMs, without a detector, a benign twin, score-level metrics, Hindi or Hinglish, or a mitigation.
- **Best use as a citation:** motivation that non-English and encoded inputs shift model behaviour. Positioning sentence: "prior multilingual/obfuscation studies measure attack compliance of chat models, not detector behaviour on benign text".
- **Terminology:** Uysal uses "prompt injection" loosely to mean direct jailbreak requests. Paper 1 should say it targets injection *detectors*, so reviewers do not conflate the two.

### Gaps
- The EDCC/AI-SS acceptance comes from the arXiv abstract page as surfaced in search snippets. I did not check a proceedings DOI.

## Q2. What is "Handa et al. 2025" (benign text through ciphers, with a false-positive rate), and does it pair harmful and benign texts?

### Takeaway
Handa et al. is arXiv 2402.10601 (v5, 14 Oct 2025; NeurIPS 2025 workshop "Reliable ML from Unreliable Data"). It is a cipher-jailbreak paper on chat LLMs, not on guards or detectors. Its over-defense experiment hand-rewrites all 50 AdvBench items into safe versions that keep the unsafe vocabulary, encodes them with 5 novel ciphers, and has a GPT-4o-mini judge label the target model's responses. The maximum reported over-defense is 40%, for gpt-oss-20b with Grid Encoding. It is the closest of the two papers to Paper 1's benign-twin idea, but the "twins" are semantic rewrites. They are not label-blind perturbations of a length-matched benign twin, no detector is scored, and no score-level metrics are reported.

### Cited Findings
- **Bibliography entry in 2609.26176:** Handa, D.; Zhang, Z.; Saeidi, A.; Kumbhar, S.; Uddin, M. N.; RRV, A.; Baral, C. (2025), "When 'Competency' in Reasoning Opens the Door to Vulnerability: Jailbreaking LLMs via Novel Ciphers," NeurIPS 2025 Workshop: Reliable ML from Unreliable Data. — [arXiv 2609.26176 HTML](https://arxiv.org/html/2609.26176)
- **Exact paper:** arXiv **2402.10601**, Arizona State University. v1 was 16 Feb 2024 and v5 was 14 Oct 2025. The arXiv title reads "...via Novel Complex Ciphers", while the NeurIPS workshop page drops "Complex". — [arXiv 2402.10601](https://arxiv.org/abs/2402.10601v4); [NeurIPS 2025 virtual page](https://neurips.cc/virtual/2025/125261)
- **Models:**
  - CipherBench decoding: gpt-oss-20b, Llama-3.1-8B-Instruct, Llama-3.1-70B-Instruct, GPT-4o, Gemini-1.5-Flash.
  - Jailbreaks: the same five plus GPT-5.
  - No guard or moderation classifier (e.g. Llama Guard) is evaluated.
  - [arXiv HTML 2402.10601v5](https://arxiv.org/html/2402.10601v5)
- **Ciphers:**
  - CipherBench uses 10. Common: Base64, ROT-13, Pig Latin, LeetSpeak. Uncommon: Keyboard Cipher, Upside-Down, Word Reversal. Novel: Word Substitution, Grid Encoding, ASCII Art.
  - The ACE attack uses 5: Keyboard, Upside-Down, Word Reversal, Grid Encoding, Word Substitution.
  - LACE layers Word Substitution with ROT-13, Keyboard, Grid or Word Reversal.
  - [arXiv HTML 2402.10601v5](https://arxiv.org/html/2402.10601v5)
- **CipherBench data:** 240 safe instances (120 short, 120 long; questions and declaratives), with randomized-character controls. It is scored for **decoding accuracy (DSR)**, not refusal. Average DSR was common 35.95%, uncommon 21.53% and novel 21.87%. Randomized-character text cut DSR by an average of 78.82%. — [arXiv HTML 2402.10601v5](https://arxiv.org/html/2402.10601v5)
- **Attack results:**
  - gpt-oss-20b: ACE ASR 0.60 (Upside-Down); LACE ASR 0.72 (Keyboard + Word Substitution).
  - GPT-4o: ACE ASR 0.40 (Word Reversal, Word Substitution, Grid).
  - GPT-5: ACE 0.00 on all ciphers; LACE at most 0.08.
  - Judge: GPT-4o-mini (temperature 0), validated on 50 items with average Cohen's kappa 0.68.
  - [arXiv HTML 2402.10601v5](https://arxiv.org/html/2402.10601v5)
- **Over-defense experiment, construction:** the authors "manually modified all 50 samples of AdvBench", keeping the unsafe words but reframing each query as safe. They then tested the modified set across the five ACE ciphers. — [arXiv HTML 2402.10601v5](https://arxiv.org/html/2402.10601v5)
- **Over-defense experiment, measurement:** they report "the percentage of responses that were incorrectly flagged as unsafe". The flagging is done by the GPT-4o-mini judge on the target LLM's response. It is not a guard's decision on the input. — [arXiv HTML 2402.10601v5](https://arxiv.org/html/2402.10601v5)
- **Over-defense results:**
  - Fig. 5 covers GPT-5, gpt-oss-20b, GPT-4o and Gemini-1.5-Flash, with no Llama models.
  - The only exact number in the text is a maximum of **40% for gpt-oss-20b under Grid Encoding**.
  - Gemini-1.5-Flash showed low over-defense because it decoded poorly. GPT-4o was most over-defensive on Word Reversal and Word Substitution. GPT-5 was described as most robust.
  - There is no per-model table in the text.
  - [arXiv HTML 2402.10601v5](https://arxiv.org/html/2402.10601v5)
- **Judge caveat from the authors:** the gpt-oss-20b Grid outputs contained a nuanced caution, and the judge "fails to notice this nuanced output carefully and labels this as overdefensive". The 40% may therefore be overstated. — [arXiv HTML 2402.10601v5](https://arxiv.org/html/2402.10601v5)
- **How 2609.26176 grades it:** the Handa over-defense row is graded "B3", the highest grade in its Appendix B.1 table. A first pass had scored it B2 from CipherBench alone. — [arXiv 2609.26176 HTML](https://arxiv.org/html/2609.26176)
- **What 2609.26176 says Handa lacks:** the refusal rate on the CipherBench benign corpus "is not reported". — [arXiv 2609.26176 HTML](https://arxiv.org/html/2609.26176)
- **Pairing:** the benign set is a one-to-one manual rewrite of each of the 50 harmful AdvBench items, so it is implicitly paired. The paper does not state the pairing explicitly, does not length-match, and does not analyse results pair by pair. — [arXiv HTML 2402.10601v5](https://arxiv.org/html/2402.10601v5)
- **No multilingual content and no mitigation:** no mitigation is tested. The authors only call for more ciphered data in safety training. — [arXiv HTML 2402.10601v5](https://arxiv.org/html/2402.10601v5)

### Inferences
- **Overlap with claim (1): partial, conceptual only.** Handa does put a harmful-derived benign set through the same ciphers as the attacks. Paper 1 still differs on four points:
  - Its targets are detectors and guard classifiers, not chat LLM refusals.
  - Its twins are length-matched benign texts, not semantic rewrites that keep unsafe keywords. Handa's set is closer to a NotInject/XSTest-style "trigger word" contrast than a perturbation control.
  - Its families are character-level and Unicode perturbations (zero-width, soft hyphen, homoglyph, fullwidth, diacritics, spacing) plus Base64/ROT13 with scaffold controls. Handa's are word- and grid-level ciphers.
  - It applies label-blind perturbation to each pair and analyses results pair by pair.
- **Overlap with families:** Base64, ROT-13 and LeetSpeak appear in Handa's CipherBench, but only for decoding accuracy, not for over-defense. Handa's over-defense run uses only the 5 novel or uncommon ciphers. Paper 1 should cite Handa as the nearest benign-cipher over-defense measurement and say clearly that it is about generator refusal judged by an LLM, with n = 50.
- **Overlap with claims (2) to (5): none.** Handa reports no AUROC, no FPR at matched TPR and no paired joint accuracy. It has no cross-guard audit, no Hindi or Hinglish, and no canonicalization or augmentation mitigation.
- **Wording discrepancy:** 2609.26176's phrase "fraction incorrectly flagged as unsafe" could be misread as a guard FPR. In Handa it is a judge's label on a response. Paper 1 should not describe Handa as measuring guard FPR.

### Gaps
- Exact per-model and per-cipher over-defense percentages from Fig. 5 were not extractable from the text. Only the 40% maximum is stated.
- The benign rewrites are not described as released. I did not check the repository.

## Q3. Do the bibliographies (or the search) point to further work on guard false positives on obfuscated or multilingual benign inputs?

### Takeaway
Neither bibliography contains such work. Uysal cites only jailbreak, multilingual-jailbreak and cipher-attack papers, and Handa's nearest entries are cipher and multilingual *attack* papers. The search did surface **PIDS-Bench (arXiv 2609.15017, Sept 2026, IEEE Access)**, which is the closest prior work to Paper 1 and must be cited and differentiated. It evaluates prompt-injection *detectors* for over-defense and obfuscation, uses leetspeak, homoglyph and zero-width transforms, and tests hard-negative augmentation. But it applies obfuscation to attacks only ("benign FPR is undefined"), has no pairing, is English-only, and does not test canonicalization.

### Cited Findings
- **Uysal's bibliography:**
  - Multilingual-jailbreak papers: Yong et al., low-resource languages jailbreak GPT-4; Deng et al., multilingual jailbreak challenges.
  - A cipher attack: Yuan et al., CipherChat.
  - Evaluation papers: StrongREJECT, HarmBench.
  - Lan et al. on prompt-injection detection.
  - None is about guard false positives or over-refusal.
  - [arXiv HTML 2606.29602v1](https://arxiv.org/html/2606.29602v1)
- **Handa's bibliography:**
  - Cipher and encoding attacks: Yuan et al. 2023 (CipherChat); Wei et al. 2024 (Jailbroken, Base64); Jiang et al. 2024 (ArtPrompt).
  - Multilingual jailbreaks: Yong et al. 2023; Deng et al. 2023.
  - Others: JailbreakBench, JailJudge, and Xie et al. 2024 (online safety analysis).
  - It does not cite XSTest, OR-Bench or Llama Guard, and none of these entries measures false positives on benign encoded or multilingual text.
  - [arXiv HTML 2402.10601v5](https://arxiv.org/html/2402.10601v5)
- **PIDS-Bench, reference:** Shire and Kim, "PIDS-Bench: Evaluating Prompt-Injection Detectors Under Over-Defense, Obfuscation, and Distribution Shift," arXiv 2609.15017, 14 Sep 2026; journal reference IEEE Access vol. 14, 2026. — [arXiv abs 2609.15017](https://arxiv.org/abs/2609.15017)
- **PIDS-Bench, detectors:**
  - Internal: TF-IDF+LR, DistilBERT, DeBERTa-v3-FT.
  - External prompt-injection classifiers: ProtectAI DeBERTa-v3 prompt-injection v2, DeBERTa-PI.
  - Broad-safety comparators: PromptGuard 2 (86M), Llama Guard 3-1B.
  - A rule-based lower-bound reference.
  - [arXiv HTML 2609.15017v1](https://arxiv.org/html/2609.15017v1)
- **PIDS-Bench, obfuscation:**
  - Transforms: leetspeak keyword substitution, homoglyph replacement, zero-width insertion. They are applied to **attacks only**: the obfuscated set "contains only injection examples; benign FPR is undefined" (405 items). There is no obfuscated-benign set and no pairing.
  - The transforms also appear in training, so this is a seen-family test only.
  - Structural shifts (JSON wrapping, dilution, prefix mimicry) are applied to 333 benign and 333 injection seeds, but not described as paired.
  - [arXiv HTML 2609.15017v1](https://arxiv.org/html/2609.15017v1)
- **PIDS-Bench, hard-benign FPR:** 1,472 items (872 externally sourced, 600 curated).
  - At τ=0.5: DeBERTa-v3-FT 0.38±0.05; DistilBERT 0.47±0.08; TF-IDF+LR 0.41.
  - At defaults: ProtectAI 0.216; DeBERTa-PI 0.804; PromptGuard 2 0.15; Llama Guard 3-1B 0.18.
  - [arXiv HTML 2609.15017v1](https://arxiv.org/html/2609.15017v1)
- **PIDS-Bench, obfuscated-attack recall:** fine-tuned models 0.97–0.99; ProtectAI 0.906; DeBERTa-PI 0.970; PromptGuard 2 0.32; Llama Guard 3-1B 0.48. — [arXiv HTML 2609.15017v1](https://arxiv.org/html/2609.15017v1)
- **PIDS-Bench, metrics, languages and mitigation:**
  - Metrics are fixed-threshold F1, recall and FPR, plus ROC-AUC where scores exist. There are bootstrap CIs and 5 seeds.
  - It is English-only and names multilingual as future work.
  - The only mitigation is hard-negative augmentation. It nearly removes curated over-defense but not externally sourced over-defense ("provenance-sensitive over-defense"). Canonicalization or normalization is not studied.
  - No detector reaches F1 ≥ 0.95 and hard-benign FPR ≤ 0.10 together.
  - [arXiv HTML 2609.15017v1](https://arxiv.org/html/2609.15017v1); [arXiv abs 2609.15017](https://arxiv.org/abs/2609.15017)
- **PIDS-Bench's over-defense citations:** Li et al. (NotInject, benign prompts with trigger words); Kholkar and Ahuja (a context-aware benchmark covering detection and over-defense); Jacob et al. (low-FPR evaluation of detectors). — [arXiv HTML 2609.15017v1](https://arxiv.org/html/2609.15017v1)
- **2609.26176's own candidates:**
  - Fairoze et al. 2026, "Bypassing Prompt Guards in Production with Controlled-Release Prompting" (arXiv 2510.01529). It is described as noting that defences are calibrated on untransformed content, but it is an *attack* (bypass) paper, so it is fail-open evidence, not benign false positives. I read it only from the 2609.26176 description and a search snippet, not the full text.
  - Verma et al. 2025, MULTIGUARD, on multilingual moderation. Its false-positive results were not checked.
  - [arXiv 2609.26176 HTML](https://arxiv.org/html/2609.26176); [arXiv 2510.01529](https://arxiv.org/pdf/2510.01529)
- **Other hits:**
  - Zhang et al., "0%, 45%, or 99%: A Guardrail's Own Share of the Refusals It Is Credited With" (arXiv 2608.08641, Aug/Sep 2026). From the abstract it concerns attributing refusals between the guard and the model on attack inputs, with encoded and pixel-rendered attacks. Benign false positives are not mentioned in the abstract; read at abstract level only. — [arXiv abs 2608.08641](https://arxiv.org/abs/2608.08641)
  - Hackett et al., "Bypassing LLM Guardrails: An Empirical Analysis of Evasion Attacks against Prompt Injection and Jailbreak Detection Systems" (arXiv 2504.11168), on character-injection evasion of detectors. Fail-open evidence, from a search hit only. — [arXiv 2504.11168](https://arxiv.org/pdf/2504.11168)

### Inferences
- **Overall verdict:** neither Uysal nor Handa pre-empts Paper 1. Uysal has no overlap. Handa partially anticipates the *idea* of putting benign, harmful-looking text through the same ciphers. It does so for chat-LLM refusal with n = 50, an LLM judge, and word or grid ciphers, without score-level paired metrics, detectors, Hindi, or mitigations.
- **PIDS-Bench is the real threat to claim framing** and should be in Related Work with explicit contrasts:
  - Claim (1): it obfuscates attacks only, so obfuscated-benign FPR is undefined. Paper 1's benign twins fill exactly that gap.
  - Claim (2): it uses fixed thresholds, not FPR at the clean condition's TPR or paired joint accuracy.
  - Claim (3): it has only 3 transform families and no fail-closed vs fail-open split per family. Its numbers, though, already show fail-open for PromptGuard 2 and Llama Guard 3-1B on obfuscated attacks.
  - Claim (4): it is English-only.
  - Claim (5): it uses hard-negative (not benign-twin) augmentation, has no canonicalization, and tests seen families only (transforms appear in training). Paper 1's held-out-family evaluation and canonicalization comparison remain novel. Its provenance-sensitive over-defense finding is a useful foil.
- **Cross-check:** PIDS-Bench's ProtectAI and PromptGuard 2 hard-benign FPRs (0.216 and 0.15) are a published baseline for Paper 1's clean-condition FPRs on the same guards.

### Gaps
- I did not determine whether 2609.26176 itself cites PIDS-Bench; the first fetch did not list it among the relevant references.
- Not checked:
  - PIDS-Bench's per-transform breakdown (leetspeak vs homoglyph vs zero-width), which sits in the unread second half of the HTML.
  - Whether PIDS-Bench's ROC-AUC is reported per condition.
  - MULTIGUARD's false-positive results on benign multilingual text.
  - Kholkar & Ahuja and Jacob et al., cited in PIDS-Bench, which should be screened for obfuscated or multilingual benign false-positive measurement.
- I found no paper measuring guard false positives on Hindi, romanized Hindi or Hinglish benign text in either bibliography or the searches here. This is not a full search of Indic guard benchmarks.
