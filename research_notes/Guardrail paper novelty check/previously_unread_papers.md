# Five previously unread papers: overlap check against Paper 1 (over-defense of prompt-injection detectors under paired benign-twin perturbation)

Paper 1 claims, used as the yardstick below:
(1) paired benign-twin perturbation protocol (label-blind zero-width, soft hyphen, leetspeak, homoglyph, Base64/ROT13 wrapping with scaffold controls, fullwidth, diacritics, letter spacing on attacks and on length-matched benign twins);
(2) paired joint accuracy, within-condition AUROC, FPR at a reference TPR;
(3) cross-guard audit of fail-closed (over-blocking) vs fail-open (evasion) behaviour under perturbation;
(4) native-speaker Hindi/Hinglish over-defense benchmark;
(5) script-aware canonicalization vs benign-twin augmentation as mitigations.

Reading status: 2610.03448, 2608.01373 and 2605.23196 were read in arXiv HTML (2605.23196 only partly: the HTML is 137k characters and the extraction tool did not surface every table cell). 2608.08641 was read in v1 HTML; the v2 HTML returned 404, so v2-only content (new title, "four other released harnesses" audit) comes from the v2 abstract page only. Fairoze et al. was read from the v4 PDF (text extracted locally); Table 5 columns were garbled in extraction, so only numbers restated in the running text are cited.

## Q1. arXiv 2608.01373, "The Boy Who Cried Wolf": what does it do, and does it study benign perturbed text or injection detectors?

### Takeaway
It is a white-box, optimisation-based attack that adds imperceptible perturbations to benign images so multimodal content-safety guards (Llama-Guard-3-Vision etc.) reject benign requests (about 78-84% ASR). It studies neither text perturbations nor prompt-injection detectors. Overlap with Paper 1 is low. It is useful as the "adversarially induced false positive" counterpoint to Paper 1's non-adversarial, label-blind perturbations.

### Cited Findings
- Title "The Boy Who Cried Wolf: Adversarial Misclassification of Safe Inputs as Unsafe in Multimodal Guardrails". Authors Shuo Shi, Rui Yin, Naen Xu, Jiahao Chen, Chunyi Zhou, Tianyu Du, Zhihui Fu, Jun Wang, Zhaoxiang Wang, Shouling Ji. arXiv v1 2 Aug 2026; comments field says "Accepted by KDD 2026". — [arXiv abs](https://arxiv.org/abs/2608.01373)
- Method: "Unsafe Induction Attacks" perturb benign images under an L-infinity bound (eps = 8/255 or 16/255). "Unsafe Semantic Distillation" (USD) aligns the perturbation with a manifold of unsafe-image representations (built from HolisticSafeBench and VHD11K) so that it works whatever the user's text prompt is. — [arXiv HTML](https://arxiv.org/html/2608.01373v1)
- Threat model: white-box access to open-weight guard weights. The attacker is a competitor who seeds perturbed images publicly and waits for users to include them in requests, producing a "logical denial of service". — [arXiv HTML](https://arxiv.org/html/2608.01373v1)
- Only the image is perturbed. The user text prompts (GPT-4o-mini-generated, "Strict Safety", benign) are not modified. — [arXiv HTML](https://arxiv.org/html/2608.01373v1)
- Guards evaluated: Llama-Guard-3-Vision, LLaVA-Guard-v1.2, Qwen-Guard-v1.2, ShieldVLM. These are multimodal content-safety guards, not prompt-injection detectors. — [arXiv HTML](https://arxiv.org/html/2608.01373v1)
- Data: 100 benign images each from TextVQA and VQAv2, pre-filtered to be judged safe by Llama Guard 3 Vision. — [arXiv HTML](https://arxiv.org/html/2608.01373v1)
- Metric: ASR is the percentage of benign images classified unsafe after perturbation, in three variants: ASRs (shadow prompts), ASRg (10 generic questions) and ASRr (10 realistic image-specific requests, the primary metric). — [arXiv HTML](https://arxiv.org/html/2608.01373v1)
- Key numbers:
  - Llama-Guard-3-Vision USD ASRr is 78.4 / 82.8 (TextVQA, eps 8/255 and 16/255) and 80.5 / 84.3 (VQAv2).
  - Best baseline CoA reaches 62.2% (TextVQA, 16/255), a 20.6 pp gap to USD.
  - Clean-image ASR is 0.0.
  - Cross-model transfer is only 0.7-3.7%, against 75.6-85.9% white-box.
  - Input preprocessing (JPEG q75, average smoothing, Gaussian blur) cuts ASRr from 78.4 to between 61.4 and 71.2 but "does not eliminate the threat".
  - [arXiv HTML](https://arxiv.org/html/2608.01373v1)
- No text-only prompt-injection detectors are evaluated, and no Unicode, encoding or multilingual text perturbations appear. — [arXiv HTML](https://arxiv.org/html/2608.01373v1)

### Inferences
- No overlap with claims (1), (2), (4) or (5). It touches claim (3) only in spirit: both papers show guards can fail closed on benign inputs. The mechanisms differ in kind. This paper uses gradient-optimised, per-model adversarial image noise. Paper 1 uses label-blind, deterministic text transforms that occur naturally (formatting, transliteration, obfuscation habits) and apply identically to attacks and benign twins.
- Cite it in related work as evidence that "false-positive attacks" on guards are an emerging concern. Paper 1 can argue that over-blocking does not need an adversary, because benign perturbations a user produces unintentionally are enough. The paper's own 0.7-3.7% transfer suggests its effect is model-specific, while Paper 1's perturbations are model-agnostic by construction.

### Gaps
- I did not verify whether the KDD 2026 acceptance is reflected in the KDD proceedings; the only source is the arXiv comment.

## Q2. arXiv 2608.08641, "A Guardrail's Own Share of the Refusals": what does it measure, and does it use perturbed or multilingual benign inputs?

### Takeaway
It is a measurement and methodology paper on attributing refusals in a defended jailbreak pipeline. It asks what fraction of refusals comes from the guard gate rather than the target model's own alignment, and shows that share can be 0%, about 41-45%, or 99% depending on the attack channel and on what text the evaluation harness feeds the defense. It measures benign over-refusal only on ORBench (English, unperturbed). Its limitations section explicitly says benign inputs that look like encodings, including multilingual text, are untested. Overlap with Paper 1 is low, and the paper names a gap that Paper 1 fills.

### Cited Findings
- The v2 title (24 Sep 2026) is "0%, 45%, or 99%: A Guardrail's Own Share of the Refusals It Is Credited With". Authors Haoyu Zhang, Xiangchen Guan, Yang Chen, Haowen Xu, Shibo Zheng, Xiao Luo, Zhuoxi Wang, Yi Feng, Mohammad Zandsalimy, Shanu Sushmita. v1 was 9 Aug 2026. The comments field says 34 pages (7 main), 3 figures, 23 tables, with no venue. — [arXiv abs](https://arxiv.org/abs/2608.08641)
- v1 carried a different title, "Whose Refusal Is It? The Unmeasured Contribution of Black-Box Multimodal Guardrails", and names no venue. — [arXiv HTML v1](https://arxiv.org/html/2608.08641v1)
- Measurement: guard blocks are counted by exact string match on the guard's canned refusal. Model refusals among guard-passed prompts are counted by a refusal judge (gpt-5-mini). Share = guard / (guard + model). The two counts are disjoint because a block replaces the response. — [arXiv HTML v1](https://arxiv.org/html/2608.08641v1)
- Setup:
  - Guards and defenses: wildguard (main text guard), llama-guard-3-8b, guardreasoner-vl-7b, ECSO, SemanticSmooth, SAGE.
  - Targets: internvl3-8b and pixtral-12b for the decomposition, plus gemini-2.5-flash / flash-lite, gpt-4o-mini, claude-sonnet-4-6 and qwen3-vl-8b-instruct elsewhere.
  - Harmful prompts: HarmBench (100 per cell). Utility: the JailbreakBench benign split. Gate benign sets: ORBench-hard and ORBench-1k.
  - [arXiv HTML v1](https://arxiv.org/html/2608.08641v1)
- Encodings are semantic attack transforms (a code-completion template, MathPrompt-style set theory, formal logic), not character-level obfuscation. The extracted text does not mention Base64. Image channel variants: payload rendered as a typographic image, payload duplicated in text and image, and a content-free decoy image. — [arXiv HTML v1](https://arxiv.org/html/2608.08641v1)
- Key numbers (wildguard, 100 prompts per cell):
  - Payload in image: 0/100 guard blocks, guard share 0%.
  - Encoded text as sent: 28-30 guard blocks against 34-44 model refusals, share 41-45%.
  - Defense reads the unencoded request: 98 guard blocks, share 99%.
  - [arXiv HTML v1](https://arxiv.org/html/2608.08641v1)
- v2 adds that the reference implementation builds every stage from one prompt field. An audit of "four other released harnesses and the benchmark" found the same structural gap. In an ablation, the regeneration stage, not the harm-verdict stage, carried the whole effect. This is from the abstract only. — [arXiv abs v2](https://arxiv.org/abs/2608.08641)
- Benign and over-defense findings:
  - The discussion describes "A guard that blocks 76-81% of adversarially-hard benign traffic". On one model family, the configuration with the best safety number "refuses 74-100% of benign traffic".
  - The two benign sets "disagree by a factor of six on false-positive rate", so the authors claim only qualitative guard facts.
  - Text guards block 0/100 benign image inputs.
  - An over-refusal judge failed on every benign cell in one round.
  - [arXiv HTML v1](https://arxiv.org/html/2608.08641v1)
- Limitations state that "benign inputs that superficially resemble encodings (mathematical, code-heavy, or multilingual text) are untested" and that benign utility was measured on unencoded prompts only. — [arXiv HTML v1](https://arxiv.org/html/2608.08641v1)
- It cites Shi et al. (2026), i.e. "Boy Who Cried Wolf", as prior work on perturbed benign images, and gives that work's clean false-positive rate as 0.0-0.4%. — [arXiv HTML v1](https://arxiv.org/html/2608.08641v1)

### Inferences
- No overlap with claims (1), (2), (4) or (5). The paper concerns jailbreak/harm guards (wildguard, Llama Guard), not prompt-injection detectors. Its "encodings" are attacker-side semantic transforms, and it has no paired benign twins.
- It is useful to Paper 1 in two ways:
  - It shows a peer group explicitly flagging benign encoded-looking and multilingual inputs as an untested over-defense risk, a gap Paper 1's twin protocol and Hindi/Hinglish set address directly.
  - Its finding that the reported guard share depends on which text the harness feeds the guard supports Paper 1's insistence on label-blind, identical transforms applied at the guard's input.
- Its 76-81% benign block rate on ORBench-hard is for a harm guard on adversarially selected over-refusal prompts. It is not comparable to Paper 1's FPR at reference TPR.

### Gaps
- v2 full text could not be fetched (HTML 404). The identities of the "four other released harnesses" and the v2 ablation numbers are unverified beyond the abstract.
- Per-guard ORBench block rates were not surfaced in the parts I read.

## Q3. arXiv 2605.23196, "Prompt Overflow": what is it, and is it relevant?

### Takeaway
It is a fail-open evasion attack on prompt-injection and toxicity guards. Malicious tokens are dispersed at low density across an overlong prompt, so each 512-token inspection window scores benign while the downstream LLM still reconstructs the instruction. It uses the same detector family as Paper 1 (Prompt Guard 2 22M/86M, ProtectAI DeBERTa v2) but no benign twins, no character-level perturbations, no multilingual data and no FPR measurement. It is relevant only to the evasion half of claim (3). Overlap is low.

### Cited Findings
- Title "Prompt Overflow: What the Guardrail Inspects Is Not What the Model Infers". Authors Yuanbo Zhou, Changjia Zhu, Junyu Wang, Xu He, Yan Zhai, Kun Sun, Mingkui Wei, Junjie Xiong. arXiv 22 May 2026, cs.CR, 18 pages, 8 figures. No venue is listed. — [arXiv abs](https://arxiv.org/abs/2605.23196)
- Guards:
  - ProtectAI DeBERTa-v3 prompt-injection v2.
  - meta-llama/Llama-Prompt-Guard-2-86M and Prompt Guard 2 22M.
  - ibm-granite/granite-guardian-hap-125m, a toxicity classifier.
  - Inspection is either non-overlapping chunking or a sliding window (512 length, stride 256), with max-pooling and threshold 0.5.
  - [arXiv HTML](https://arxiv.org/html/2605.23196v1)
- Attack knobs: density K (4-16 original tokens per segment), layouts (Head, Tail, Interleave), and fillers ("Blank", "Think", and *Pride and Prejudice* prose). A binary-search procedure estimates the window size from allow/block feedback alone. — [arXiv HTML](https://arxiv.org/html/2605.23196v1)
- Data:
  - 5,000 malicious prompts per injection detector, from a Hugging Face prompt-injection benchmark (Liu et al. 2024b), and 10,000 RealToxicityPrompts for Granite.
  - Verified subsets correctly flagged in short form: DeBERTa v2 1,311, PG2-86M 1,266, PG2-22M 890, Granite 1,510.
  - Benign fillers score below 0.01 on all guards.
  - [arXiv HTML](https://arxiv.org/html/2605.23196v1)
- Key numbers:
  - PG2-86M, Interleave, sliding window: 100.0% bypass at K=4 and 99.9% at K=16. Tail: 49.5% falling to 27.3%.
  - DeBERTa v2: 0% with Blank filler, but 92.3% at K=4 with novel-prose filler.
  - Granite: about 99-100% bypass throughout.
  - Gemini 3 Pro recognised the malicious intent "in all 200 cases".
  - [arXiv HTML](https://arxiv.org/html/2605.23196v1)
- Proposed defenses:
  - Adversarial training (the authors note it may raise false positives on benign long text), view alignment, and stateful aggregation.
  - A "contiguity-gated excess-sum" aggregator with background threshold 0.1093, the 99th percentile of 2,000 benign packed prompts, evaluated on 1,000 held-out instances.
  - The excerpt gives no benign FPR numbers. Appendix F shows a benign prompt where one window scored 0.9990 on the phrase "your previous rules and".
  - [arXiv HTML](https://arxiv.org/html/2605.23196v1)
- No Unicode, encoding, or multilingual content was found in the text examined. — [arXiv HTML](https://arxiv.org/html/2605.23196v1)

### Inferences
- Relevant only as a fail-open comparator for claim (3). It confirms that the same open PI detectors Paper 1 audits can be evaded by length and dilution rather than by character obfuscation.
- The benign 0.9990 window spike in its Appendix F is anecdotal support for Paper 1's thesis that PI detectors over-fire on benign surface cues. Paper 1 should not lean on it beyond an aside.
- Paper 1 should control for its own length effects (it already length-matches twins) and could cite this work to justify keeping perturbed inputs under the 512-token window, so that truncation does not confound the results.

### Gaps
- The meaning of the "Novel Scripts" column in Table 2 is not confirmed. It most likely means novel-prose filler, but the extraction could not verify this.
- No quantitative benign FPR for the proposed defense was surfaced.

## Q4. Fairoze et al., USENIX Security 2026 ("controlled-release prompting"): what does it propose and evaluate, and does it involve guard over-blocking or encoded inputs?

### Takeaway
"Bypassing Prompt Guards in Production with Controlled-Release Prompting" (Fairoze, Garg, Lee, Wang) is a fail-open evasion paper. It encodes jailbreaks with a substitution cipher (timed-release) or a long-context spacing scheme (spaced-release). Lightweight guards cannot decode these, but the main LLM can, which bypasses Gemini, DeepSeek, Grok and Mistral Le Chat. It evaluates 14 open-weight guards on encoded and controlled-release attacks. It does not measure over-blocking of benign encoded inputs. It does argue in prose that blocking all ciphers or encodings is infeasible partly because benign users routinely use encodings and transliteration. Overlap is low to moderate: the evasion half of claim (3) and the encoding part of claim (1), with no benign twins.

### Cited Findings
- arXiv 2510.01529: v1 2 Oct 2025, v2 7 Oct 2025, v3 2 Jun 2026, v4 10 Jun 2026. The comments field reads "Accepted to USENIX Security 2026". Categories cs.LG and cs.CR. — [arXiv abs](https://arxiv.org/abs/2510.01529)
- The v4 PDF carries the footer "Appeared in USENIX Security 2026." — [arXiv PDF v4](https://arxiv.org/pdf/2510.01529v4)
- Motivation: an empirical instantiation of Ball et al.'s impossibility result, which says no prompt filter running much faster than the protected model can universally detect adversarial prompts. The attack exploits resource asymmetry, not a capability gap. — [arXiv PDF v4](https://arxiv.org/pdf/2510.01529v4)
- Mechanism (high level only):
  - Timed-release applies a character-level substitution cipher, forcing roughly O(n) sequential decoding.
  - Spaced-release spreads the payload across a long context; Figure 2 puts success at about 10,000+ prompt tokens.
  - Timed-release success thresholds are around 800 tokens on Gemini 2.5 Flash.
  - [arXiv PDF v4](https://arxiv.org/pdf/2510.01529v4)
- Production results: 12/12 malicious intents for three platforms and 11/12 for Mistral Le Chat, where baselines fail. It also extracts copyrighted text from Gemini 2.5 Pro (timed-release averages 89.4% containment, 92.8% TF-IDF, 91.3% sentence-transformer similarity). — [arXiv PDF v4](https://arxiv.org/pdf/2510.01529v4)
- Guard survey:
  - Models: Llama Prompt Guard 1, Prompt Guard 2 (86M, 22M), ProtectAI (184M DeBERTa), PIGuard, ShieldGemma (2B), YuFeng-XGuard 0.6B/8B in instant and thinking modes, Qwen3-32B and DeepSeek-V3 (instant), and Qwen3-32B thinking and DeepSeek-R1 (thinking).
  - Benchmark: 3,930 balanced Guardrails AI jailbreak/benign prompts.
  - Attacks: 4,000 attack prompts per type (100 intents x 40 jailbreak templates), in five types: raw, jailbreak, encoding, PTLP and PSLP.
  - Metrics: ROC-AUC and F1, plus mean detection score per attack type.
  - [arXiv PDF v4](https://arxiv.org/pdf/2510.01529v4)
- Key guard findings:
  - Purpose-built classifiers have similar benchmark ROC-AUC (0.83-0.93) but "fail differently".
  - Prompt Guard 2 "shows severe regression on encoding and controlled-release attacks (detection 0.02-0.23)" against Prompt Guard 1.
  - PIGuard has the highest benchmark ROC-AUC (0.925) but is insensitive to 3 of 5 attack types.
  - YuFeng-XGuard instant detection is near zero on encoding (0.01 and 0.05) and on PTLP/PSLP.
  - DeepSeek-R1 detects all attacks but at about 70x the latency and thousands of reasoning tokens.
  - "Finding 3: Benchmark metrics poorly predict deployment security."
  - [arXiv PDF v4](https://arxiv.org/pdf/2510.01529v4)
- On over-blocking, the paper argues that blocking all prompts containing ciphers or encodings is "neither feasible nor reliable". Reasons given:
  - "encoding tasks are routine benign operations" (debugging, cryptography students, CTFs, and "multilingual users work with transliteration").
  - The encoding space (substitution, transposition, base64, ROT13, and more) is unbounded.
  - This is argued, not measured. No benign encoded set or FPR on benign encoded inputs is reported. The PIGuard description notes its over-defense design goal.
  - [arXiv PDF v4](https://arxiv.org/pdf/2510.01529v4)
- Recommended defenses: output filtering (the decode step puts the malicious text into intermediate output), filtering reasoning tokens, and not relying on input filters as the sole defense. — [arXiv PDF v4](https://arxiv.org/pdf/2510.01529v4)

### Inferences
- Overlap with Paper 1 is limited to the fail-open side of claim (3) and to "encoded wrapping" as a perturbation family in claim (1). Its encodings are attacker-chosen ciphers with explicit decoding instructions, with no length-matched benign counterparts and no scaffold-only control. Paper 1's Base64/ROT13 arm with scaffold controls tests something different: whether the guard reacts to the wrapper itself on benign text.
- Its unmeasured claim that benign encoding and transliteration use is common is a direct hook for Paper 1. Paper 1 provides the missing measurement (fail-closed rates on benign encoded or transliterated twins, and Hinglish).
- Its "benchmark metrics poorly predict deployment security" finding parallels Liu (Q5). Paper 1 should cite both and frame its perturbation audit as a third axis, robustness symmetry, rather than claiming "benchmarks mislead" as new.
- The Prompt Guard 2 regression on encodings is a fail-open data point that Paper 1's audit can corroborate or contrast under its label-blind protocol.

### Gaps
- I could not confirm the paper in the official USENIX Security 2026 program pages through search. The evidence is the arXiv comment and the v4 PDF footer. Search results showed only a third-party program blog.
- Per-guard Table 5 numbers were garbled in PDF extraction. Only values restated in the prose are cited.
- An HTML fetch of the paper was refused by the fetch tool's content filter, so the PDF was used.

## Q5. arXiv 2610.03448, "Passing the Test You Trained On": detectors, benign sources, FPR results, contamination, perturbation or multilingual evaluation

### Takeaway
This is the closest recent comparator to Paper 1's cross-guard audit. It is a single-author (Zhuowen Liu, 2 Oct 2026) re-evaluation of 15 open prompt-injection detectors plus 2 LLM judges on LLM-free replayed benign and injected tool outputs from AgentDojo and tau-bench, and on BIPIA. It reports default-threshold FPR, AUROC, TPR at 1% FPR, and task-level block rates, and finds:
- benchmark rankings do not transfer (Kendall tau = 0.01 between BIPIA and AgentDojo);
- benign FPR rankings do transfer (tau = 0.67);
- verbatim training/test contamination exists (PIGuard contains 65/75 BIPIA training-half text attacks);
- formatting alone moves FPR substantially.

It has no character perturbations, no encodings, no multilingual evaluation and no benign twins. Overlap is moderate on claims (2) and (3), specifically the "over-defense varies widely across guards" framing. Claims (1), (4) and (5) remain uncovered.

### Cited Findings
- Title "Passing the Test You Trained On: Re-evaluating Prompt-Injection Detectors for LLM Agents". Single author Zhuowen Liu. v1 2 Oct 2026, cs.CR / cs.CL. 12 pages, 5 figures, 4 tables. Code at github.com/lzwhehe/benign-instruction-bench. No venue listed. — [arXiv abs](https://arxiv.org/abs/2610.03448)
- The 15 detectors (year, size, HF ID as printed, some truncated):
  - JasperLS deberta-v3-base-injection (2023, 184M)
  - ProtectAI v1 (2023, 184M)
  - ProtectAI v2 (2024, 184M)
  - ProtectAI v2-small (2024, 142M)
  - TestSavant-L (2024, 184M)
  - Prompt Guard 1 (meta-llama/Prompt-Guard-86M, 279M)
  - PIGuard (leolee99/PIGuard, 2025, 184M)
  - Prompt Guard 2 22M (71M)
  - Prompt Guard 2 86M (279M)
  - Qualifire prompt-injection-sentinel (396M)
  - Sentinel v2 (rogue-security, 596M)
  - Sheltron prompt-guard-68m (2026, trained on agent data)
  - Prismor prompt-guard-1.5b (2026)
  - Wolf Defender (patronus-studio, 2026, 308M, card reports AgentDojo-derived evaluation)
  - Horizon-Labs guard-base (2026, 308M, trained on agent data)

  A Sheltron "+task" variant passes the user request in a trusted segment. InjecGuard gave identical scores to PIGuard and is reported once. deepset/deberta-v3-base-injection and fmops/distilbert-prompt-injection were excluded because they "flagged all benign README chunks". CodeIntegrity was gated. — [arXiv HTML](https://arxiv.org/html/2610.03448v1)
- LLM judges: Qwen2.5-7B-Instruct and Llama-3.1-8B-Instruct, both NF4 4-bit and task-aware. The 4-bit Qwen matches bf16 within 0.02 AUROC. — [arXiv HTML](https://arxiv.org/html/2610.03448v1)
- Benign and injected sources:
  - General text: 7,504 chunks of 80-220 words, about 2,500 each from GitHub READMEs, AESLC business emails and FineWeb-Edu.
  - AD-Clean: 339 outputs from 97 tasks in the AgentDojo workspace, travel, banking and slack suites, ground-truth tool calls replayed with no LLM.
  - AD-Matched: 585 benign and 432 injected outputs over 3 templates.
  - AD-Shift: 975 benign and 720 injected outputs over 5 other templates.
  - TB-Clean: 1,533 benign outputs from all 675 tau-bench retail and airline tasks.
  - TB-Matched: 584 injected outputs, InjecAgent attacks placed in product names.
  - BIPIA: 1,200 benign and 2,435 injected, test-half attacks only.
  - [arXiv HTML](https://arxiv.org/html/2610.03448v1)
- Paired design: injected outputs are labelled by "differential replay", comparing each injected output with the same call's clean output. Benign and injected samples therefore share the same tool calls, a matched-pair construction. — [arXiv HTML](https://arxiv.org/html/2610.03448v1)
- Metrics: FPR and TPR at default threshold 0.5, AUROC, TPR at 1% FPR (threshold chosen on the same benign set, which the paper notes favours detectors), task-level block rate, 95% percentile bootstrap CIs (1,000 resamples), and Kendall tau. — [arXiv HTML](https://arxiv.org/html/2610.03448v1)
- FPR on benign tool outputs at default threshold (AgentDojo / tau-bench, plus AgentDojo task block rate where reported):

  | Detector | AgentDojo FPR | tau-bench FPR | AgentDojo task block rate |
  |---|---|---|---|
  | Horizon-Labs | 0.0% | 0.7% | 0.0% |
  | Wolf Defender | 0.9% | 0.0% | 3.1% |
  | PG2-86M | 0.6% | 0.0% | 2.1% |
  | PG2-22M | 0.0% | 0.0% | 0.0% |
  | Qualifire | 0.9% | 0.0% | |
  | Sentinel v2 | 2.1% | 0.5% | |
  | Sheltron | 10.6% | 4.4% | |
  | Sheltron +task | 26.0% | 69.7% | |
  | Prismor | 6.5% | 46.2% | |
  | ProtectAI v2 | 30.1% | 66.9% | 69.1% |
  | PIGuard | 29.5% | 11.0% | 59.8% |
  | Prompt Guard 1 | 31.9% | | |
  | JasperLS | 78.5% | 93.1% | |

  The judges' tau-bench FPR is Qwen 4.4% and Llama 5.4%. — [arXiv HTML](https://arxiv.org/html/2610.03448v1)
- TPR at 1% FPR (AD-Matched / AD-Shift / TB-Matched / BIPIA):

  | Detector | AD-Matched | AD-Shift | TB-Matched | BIPIA |
  |---|---|---|---|---|
  | Horizon-Labs | 82.2% | 87.9% | 100.0% | 37.7% |
  | Wolf Defender | 73.8% | 83.9% | 90.8% | 3.5% |
  | Prismor | 72.2% | 79.4% | 15.2% | 4.0% |
  | PG2-86M | 69.4% | 78.8% | 57.9% | 10.4% |
  | PG2-22M | 60.9% | 63.6% | 60.8% | 31.7% |
  | Sheltron | 20.1% | 26.4% | 95.2% | 57.2% |
  | PIGuard | 2.1% | 7.9% | 52.7% | 95.1% |
  | ProtectAI v2 | 0.5% | 0.8% | 10.1% | 0.7% |

  Judges (AD-Matched / TB-Matched / BIPIA): Qwen 57.4 / 54.3 / 14.9%, Llama 55.3 / 78.3 / 8.3%. — [arXiv HTML](https://arxiv.org/html/2610.03448v1)
- Rank transfer (Kendall tau):
  - BIPIA vs AD-Matched: 0.01 (p = 1.00)
  - AD vs tau-bench: 0.28 (p = 0.17)
  - BIPIA vs tau-bench: 0.31 (p = 0.11)
  - FPR rank, AD vs tau-bench: 0.67 (p = 0.001)
  - [arXiv HTML](https://arxiv.org/html/2610.03448v1)
- Contamination and training-data findings:
  - PIGuard's published training split contains 1,116 full BIPIA inputs. These cover 65/75 text attacks and 6/50 code attacks from BIPIA's training half, plus 31% of clean emails, 22% of clean code and 0.3% of clean tables. The test half has 0/75 and 0/50.
  - Restricting to test-half attacks lowers PIGuard's BIPIA TPR at 1% FPR only from 97.9% to 95.1%.
  - PIGuard's training data also contains 53/62 InjecAgent attacks, as 111 short prompts. It detects 52.1% of tau-bench injections using trained-on InjecAgent attacks and 55.8% using unseen ones.
  - Horizon-Labs' public training sources contain no BIPIA, AgentDojo or InjecAgent strings.
  - The overlap audits are verbatim-only lower bounds.
  - [arXiv HTML](https://arxiv.org/html/2610.03448v1)
- Format effects:
  - Stripping README markup cuts PIGuard README FPR from 24.6% to 5.6%.
  - Removing YAML keys cuts PIGuard AD-Matched FPR from 20.0% to 6.7%, while TPR at 0.5 moves from 73.1% to 74.3%.
  - Declaring the input as tool_result cuts Sheltron tau-bench FPR from 85.6% to 4.4%.
  - Sheltron's task segment raises AUROC from 0.86 to 0.91 but drops TPR at 1% FPR from 20.1% to 9.0%.
  - [arXiv HTML](https://arxiv.org/html/2610.03448v1)
- No encoding, Unicode, homoglyph or leetspeak perturbations and no multilingual or non-English evaluation are reported. The format manipulations change structure but do not obfuscate. The paper cites PIGuard's NotInject over-defense set but does not run a trigger-word over-defense set. — [arXiv HTML](https://arxiv.org/html/2610.03448v1)
- Recommendations: evaluate on the agent's own tool outputs, report detection at low FPR, and audit detector training data. Stated limitations: synthetic environments, static non-adaptive attacks, no commercial APIs, threshold chosen on the evaluation set, and only PIGuard and Horizon-Labs auditable for training data. — [arXiv HTML](https://arxiv.org/html/2610.03448v1)

### Inferences
- **Claim (3), cross-guard over-defense audit:** moderate overlap. Liu already shows that over-defense (benign FPR) varies by two orders of magnitude across almost the same detector set Paper 1 uses: PG1, PG2-22M/86M, ProtectAI v2, PIGuard, and likely deepset. Paper 1 cannot claim "first cross-guard over-defense audit" or "guards differ wildly in FPR". Its novelty must rest on the perturbation-induced shift: the same guard's fail-closed versus fail-open movement under identical label-blind transforms. Liu does not test that.
- **Claim (2), metrics:** partial overlap. Liu uses AUROC and TPR at a fixed FPR (1%). Paper 1 uses FPR at a reference TPR (the dual operating point), paired joint accuracy, and within-condition AUROC. Paper 1 should cite Liu's TPR at 1% FPR and the threshold-on-evaluation-set caveat, and explain why fixing TPR suits an over-defense paper. Liu's differential-replay matched pairs are a precedent for paired benign/attack construction. Paper 1's twins differ in being length-matched benign texts receiving identical perturbations, rather than clean versus injected versions of one call.
- **Claim (5), mitigation:** weak precedent. Liu's format findings (stripping markup or YAML keys sharply cuts FPR with no TPR loss) are a structural normalisation result, conceptually adjacent to Paper 1's script-aware canonicalization. Paper 1 should cite them as evidence that input normalisation reduces over-defense, while noting Liu does not address Unicode, scripts or encodings.
- **Contamination:** Liu's verbatim-overlap audit (PIGuard and BIPIA/InjecAgent) is a methodological precedent. If Paper 1 uses deepset, BIPIA or NotInject-derived data, it should run a similar contamination check or cite this as a threat to validity.
- **Shared-detector caveat:** deepset/deberta-v3-base-injection and fmops were excluded by Liu for flagging all benign README chunks. If Paper 1 includes deepset, Liu provides independent corroboration of its extreme benign FPR.
- **Claims (1) and (4):** not covered at all, so they remain the clearest novelty.

### Gaps
- I did not inspect the GitHub repo (lzwhehe/benign-instruction-bench), for example whether any perturbation or multilingual extension is planned.
- No peer-reviewed venue was identified, as of v1 (2 Oct 2026).
- Full detector HF IDs are truncated in the paper's appendix as extracted.
