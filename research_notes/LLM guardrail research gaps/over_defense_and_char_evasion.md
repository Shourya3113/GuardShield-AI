# Over-defense of injection/jailbreak detectors and character-level evasion: prior work and novelty assessment for a paired-perturbation (benign-twin) evaluation paper

Scope: (a) over-defense / false positives of prompt-injection and jailbreak detectors; (b) character-level / encoding evasion of guardrail classifiers; with focus on whether anyone evaluates perturbed BENIGN text alongside perturbed attacks. Notes compiled 2026-10-12.

Verification legend: "[verified]" = I read the paper's abstract/HTML in this session (via WebFetch). "[snippet]" = seen only in search-result snippets/secondary summaries. "[background]" = well-known paper cited from prior knowledge, arXiv ID believed correct but not re-fetched this session.

---

## Q1. Over-defense literature: what was measured and proposed, and does any of it use obfuscated/perturbed benign text?

### Takeaway
Over-defense of injection detectors is an established topic (InjecGuard/PIGuard + NotInject, ACL 2025), but it is defined as *trigger-word* bias on clean, natural-language benign text. LLM over-refusal benchmarks (XSTest, OR-Bench, PHTest, FalseReject) are also clean-text. The first works that measure benign-side false positives under perturbation/obfuscation all appeared in Aug-Sep 2026 (PIDS-Bench, HiveTraceGuard-Pro, "Refusing Everything Looks Safe"), so the gap the team targets is real but closing fast.

### Cited Findings
**InjecGuard / PIGuard / NotInject (injection-detector over-defense)**
- [verified] InjecGuard (arXiv 2410.22770, Li & Liu et al., first posted 30 Oct 2024) defines over-defense as guards "falsely flagging benign inputs as malicious due to trigger word bias"; introduces NotInject, 339 benign samples enriched with trigger words common in injection attacks; reports none of Deepset, fmops, Meta Prompt Guard, ProtectAI exceeds 60% over-defense accuracy (50% = random) — [arXiv 2410.22770](https://arxiv.org/abs/2410.22770v1)
- [verified] Proposed mitigation is the "Mitigating Over-defense for Free" (MOF) training strategy, reducing reliance on trigger words; claims +30.8% over the best existing model on benchmarks including NotInject — [arXiv 2410.22770](https://arxiv.org/html/2410.22770v3)
- [verified] Published as PIGuard at ACL 2025 (Li, Liu, Zhang, Xiao); model renamed from InjecGuard to PIGuard for licensing reasons; DeBERTa-v3-based classifier; reports +30.4% over best existing model — [ACL Anthology 2025.acl-long.1468](https://aclanthology.org/2025.acl-long.1468), [HF model card](https://huggingface.co/leolee99/PIGuard/blob/main/README.md)
- [inference from the above] NotInject's benign samples are clean natural-language sentences containing trigger words; there is no character-level or encoding perturbation of the benign side. Its unit of "over-defense" is lexical (trigger-word) not orthographic.

**PIDS-Bench (closest injection-detector competitor; Sep 2026)**
- [verified] "PIDS-Bench: Evaluating Prompt-Injection Detectors Under Over-Defense, Obfuscation, and Distribution Shift", Shire & Kim (Kookmin Univ.), arXiv 2609.15017, submitted 14 Sep 2026, listed as IEEE Access vol. 14 (2026) — [arXiv 2609.15017](https://arxiv.org/html/2609.15017)
- [verified] Detectors: TF-IDF+LR, DistilBERT, DeBERTa-v3-FT (trained in-house, 5 seeds), rule-based, ProtectAI DeBERTa-v3, DeBERTa-PI, PromptGuard 2 (86M), Llama Guard 3-1B — [arXiv 2609.15017](https://arxiv.org/html/2609.15017)
- [verified] Its obfuscation set (405 held-out injections; leetspeak, homoglyph, zero-width insertion) is ATTACK-ONLY: the paper states "This set contains only injection examples; benign FPR is undefined." — [arXiv 2609.15017](https://arxiv.org/html/2609.15017)
- [verified] Reported DeBERTa-v3-FT numbers (tau=0.5, 5-seed means): IID F1 0.9882, obfuscated recall 0.9867, hard-benign FPR 0.3825, structural-shift FPR 0.8108 — [arXiv 2609.15017](https://arxiv.org/html/2609.15017)
- [verified] Structural-shift set (JSON wrapping, prompt dilution, instruction-prefix mimicry) IS applied to 333 benign and 333 injection seeds; authors report "Structural shift is dominated by benign-side inflation". Pairs are not described as matched benign/attack twins — [arXiv 2609.15017](https://arxiv.org/html/2609.15017)
- [verified] Mitigation: hard-negative augmentation (benign examples carrying injection-associated features) "nearly eliminates over-defense on curated inputs" but leaves externally sourced over-defense largely intact ("provenance-sensitive over-defense"); threshold calibration judged insufficient; input normalization not discussed — [arXiv 2609.15017](https://arxiv.org/html/2609.15017)
- [verified] Stated open questions: "Whether detectors generalize to obfuscation strategies absent from training" — [arXiv 2609.15017](https://arxiv.org/html/2609.15017)

**HiveTraceGuard-Pro (generative guard; Sep 2026)**
- [verified] Oblakov, Sadiekh, Kokuykin (HiveTraceLab), arXiv 2609.01046, 1 Sep 2026. Training corpus applies eight obfuscation transforms (random case, symbol insertion, symbol replacement, zero-width insertion, leetspeak, Latin transliteration, keyboard "wrong_layout", phonetic substitution) "to both labels"; eval adds unseen to_lower, to_upper, informal rewriting — [arXiv 2609.01046](https://arxiv.org/html/2609.01046)
- [verified] Benign FPR: clean benign requests 0.016 (69/4,234); augmented (obfuscated) benign requests 0.139 (500/3,599); worst transform wrong_layout FPR 0.262 — [arXiv 2609.01046](https://arxiv.org/html/2609.01046)
- [verified] Key finding: across six data rounds, "improvements in recall on obfuscated harmful requests repeatedly increased over-blocking of obfuscated benign requests" (or vice versa); "None of the tested data mixtures removed this coupling." — [arXiv 2609.01046](https://arxiv.org/html/2609.01046)
- [verified] No input normalizer at inference ("the shipped path has no input normalizer") — [arXiv 2609.01046](https://arxiv.org/html/2609.01046)
- [verified] Also reports a train/eval cipher mismatch for wrong_layout; aligning ciphers cut that transform's harm FNR 0.675 -> 0.125 — [arXiv 2609.01046](https://arxiv.org/html/2609.01046)

**"Refusing Everything Looks Safe" (LLM refusal, not detectors; Sep 2026)**
- [verified] Zhang et al. (Northeastern), arXiv 2609.26176 (v2 24 Sep 2026). Argues encoded-attack benchmarks score only the harmful arm; builds {harmful, benign} x {plaintext, scaffold, encoded} cells over JailbreakBench's 100 behaviours with theme-matched benign counterparts; evaluates 4 open 7-8B instruct LLMs (Llama-3.1-8B, Qwen2.5-7B, Tulu-3-8B, Mistral-7B) — NOT guard classifiers — [arXiv 2609.26176](https://arxiv.org/html/2609.26176v2)
- [verified] Encodings: homoglyph (main), math-bold, fullwidth, zero-width, base64, tag-block; base64 and tag-block were unreadable by all models; leetspeak and ROT13 not tested — [arXiv 2609.26176](https://arxiv.org/html/2609.26176v2)
- [verified] Metric: harm gap Delta = r_harmful - r_benign and "gap lost" = Delta_plain - Delta_enc. Llama's gap falls +0.82 (plaintext) -> 0.00 (homoglyph), both arms refused at 0.99; benign refusal spread under homoglyph 0.69 vs 0.15 plaintext. Quote: "A benchmark reading only the harmful arm scores that model and one retaining a +0.61 gap identically." — [arXiv 2609.26176](https://arxiv.org/html/2609.26176v2)
- [verified] No mitigation proposed beyond a reporting recommendation (report both arms, plaintext baseline, scaffold arm); names Handa et al. 2025 "CipherBench" as the closest prior cell (benign text through ciphers, but scoring decoding accuracy) — [arXiv 2609.26176](https://arxiv.org/html/2609.26176v2)

**LLM over-refusal benchmarks (clean text)**
- [background] XSTest (Röttger et al., NAACL 2024): 250 safe prompts + contrasting unsafe prompts testing exaggerated safety; pairs are lexical/topical, not perturbation-based — [arXiv 2308.01263](https://arxiv.org/abs/2308.01263)
- [snippet/background] OR-Bench (Cui et al., ICML 2025): ~80K "seemingly toxic" benign prompts across 10 categories, a hard subset, and toxic controls; plaintext only — [arXiv 2405.20947](https://arxiv.org/html/2405.20947v2)
- [background] PHTest (An et al. 2024, "Automatic pseudo-harmful prompt generation") — pseudo-harmful benign prompts; plaintext — [arXiv 2409.00598](https://arxiv.org/abs/2409.00598)
- [background] FalseReject (2025) — over-refusal benchmark/training data with structured reasoning; plaintext — [arXiv 2505.08054](https://arxiv.org/abs/2505.08054)
- [verified] "No Free Lunch With Guardrails" (Kumar et al., Enkrypt AI, arXiv 2504.00441, Apr 2025) measures safety-vs-usability across Azure, Bedrock, OpenAI Moderation, Llama Guard, NeMo, vijil-mbert-prompt-injection etc.; obfuscation (encoded prompts) appears only in the ADVERSARIAL set; benign pseudo-harm sets (PHTest, GuardrailsAI) are unperturbed; concludes "no guardrail configuration simultaneously achieves optimal safety, utility, and usability" — [arXiv 2504.00441](https://arxiv.org/html/2504.00441v2)

**Perturbed-benign measurements on safety (content) guards**
- [verified] Hugging Face community blog (Kalyan KS, 23 May 2026) on GLiGuard, LlamaGuard3-8B, MiniGuard v0.1 with 16 character-level mutations (homoglyph, leetspeak, insertion/deletion/swap, case, token splitting, punctuation); defines "Safe ASR" = fraction of benign prompts flagged unsafe after perturbation (on AEGIS 2.0, WildGuard, ExpGuard); max Safe ASR 25% (GLiGuard), 17% (LlamaGuard3-8B), 15% (MiniGuard). Not peer-reviewed, no arXiv paper, content-safety (not injection) guards — [HF blog](https://huggingface.co/blog/kalyan-ks/llm-guardrail-models-less-robust)

### Inferences
- The "over-defense" concept for injection detectors is owned by InjecGuard/PIGuard; a new paper must frame its contribution as a *different axis* of over-defense (orthographic/encoding-induced, "format-triggered") vs NotInject's lexical "trigger-word" over-defense.
- The team's DeBERTa-v3-small observation (73-98% FPR on perturbed benign) is consistent with PIDS-Bench's DeBERTa-v3-FT structural-shift FPR of 0.81 and its 0.987 obfuscated recall with undefined benign FPR — i.e., PIDS-Bench reports exactly the "apparent robustness" number the team argues is misleading, without the benign arm that would expose it.
- HiveTraceGuard-Pro is the closest evidence that training on perturbed benign twins helps but exhibits a recall/FPR coupling; this partially pre-empts the team's mitigation claim and should be cited as a known trade-off they must engage with.

### Gaps
- I did not find any paper (peer-reviewed or preprint) that measures FPR on perturbed benign inputs across multiple public prompt-INJECTION detectors (ProtectAI, Prompt Guard 1/2, PIGuard, Deepset, Lakera, Azure Prompt Shield) for zero-width, soft-hyphen, leetspeak, Cyrillic homoglyph, Base64, ROT13. Absence of evidence after ~18 searches/fetches; not exhaustive.
- Could not read HiveTraceGuard-Pro's Table 13 (per-transform benign FPR) — beyond the fetched portion.
- Did not verify CipherBench (Handa et al. 2025) directly; only via the citation in 2609.26176.

---

## Q2. Character-level / encoding evasion of guardrails: do they report benign-perturbed false positives or only ASR?

### Takeaway
The evasion literature (Hackett et al. 2025, Emoji Attack, Unicode tag smuggling, CipherChat, Jailbroken, ArtPrompt, latent-collapse analyses) reports attack success / misclassification of attacks only; none of the injection-detector evasion papers I checked perturbs benign text or reports benign FPR under the same perturbation.

### Cited Findings
- [verified] Hackett, Birch, Trawicki, Suri, Garraghan (Mindgard / Lancaster), arXiv 2504.11168 (Apr 2025, rev. Jul 2025); also at ACL LLMSEC 2025 workshop as "Bypassing LLM Guardrails: An Empirical Analysis of Evasion Attacks against Prompt Injection and Jailbreak Detection Systems" — [arXiv 2504.11168](https://arxiv.org/abs/2504.11168v2), [ACL Anthology author page](https://aclanthology.org/people/william-hackett/unverified/)
- [verified] Six guards: Azure Prompt Shield, ProtectAI v1, ProtectAI v2, Meta Prompt Guard, NeMo Guard Jailbreak Detect, Vijil Prompt Injection. 12 character-injection techniques: Numbers (leet-like "H3110"), Homoglyph, Zero Width, Diacritics, Spaces, Underline Accent Marks, Upside Down, Full Width, Bidirectional Text, Deletion Characters, Emoji Smuggling, Unicode Tag Smuggling; plus 8 TextAttack AML attacks (BAE, BERT-Attack, DeepWordBug, Alzantot, TextFooler, PWWS, Pruthi, TextBugger) — [arXiv 2504.11168](https://arxiv.org/html/2504.11168v2)
- [verified] Metric is ASR = "rate at which a modified prompt injection or jailbreak sample is misclassified as benign"; datasets filtered to adversarial samples (476 injections, 78 jailbreaks); NO perturbed-benign or FPR measurement; no normalization or adversarial-training defense evaluated — [arXiv 2504.11168](https://arxiv.org/html/2504.11168v2)
- [snippet] Hackett et al. report emoji smuggling reached 100% ASR in some cases, homoglyphs and zero-width "consistently evaded with moderate success"; also show word-importance ranking from white-box models transfers to black-box targets — [arXiv 2504.11168](https://arxiv.org/html/2504.11168v1)
- [snippet] Emoji Attack (Wei, Liu, Erichson; ICML 2025): inserting emojis exploits "token segmentation bias" in Judge LLMs to reduce harm detection; reported metrics are on harmful content only; a prompt-level "filter unusual characters" defense can be bypassed by mixing emojis with other characters — [arXiv 2411.01077](https://arxiv.org/abs/2411.01077v4), [PMLR v267](https://proceedings.mlr.press/v267/wei25g.html)
- [snippet] Unicode tag smuggling (U+E0000-E007F) renders invisibly but is tokenized; practitioner defenses strip Tag block + zero-width + normalize; caveat that tag characters legitimately appear in subdivision-flag emoji (false-positive risk) — [garak docs](https://reference.garak.ai/en/stable/ascii_smuggling.html)
- [verified] Mashaido & Das, arXiv 2605.19159 (May 2026): DistilBERT/BERT-Base/BERT-Medium 4-way classifiers with homoglyphs, zero-width, emoji/punctuation noise; near-99% scores but obfuscated embeddings partly collapse onto clean manifold; "high detection performance does not imply representational robustness"; no benign-obfuscated FPR, no normalization/adversarial-training defense — [arXiv 2605.19159](https://arxiv.org/html/2605.19159)
- [verified] Zhang et al., "Unread or Unenforced?", arXiv 2609.26178 (Aug/Sep 2026): probes two open content guards' residual streams over a 19-condition encoding ladder to separate representation vs enforcement failure; finds "blocked without decoding" near zero (little evidence of a pure encoding-format detector in those guards). Abstract does not mention benign encoded twins — [arXiv 2609.26178](https://arxiv.org/abs/2609.26178)
- [background] Jailbroken (Wei, Haghtalab, Steinhardt, NeurIPS 2023): Base64, ROT13, leetspeak etc. as "competing objectives / mismatched generalization" jailbreaks; includes harmless control prompts scored for capability, not refusal — [arXiv 2307.02483](https://arxiv.org/pdf/2307.02483); the latter point confirmed by [arXiv 2609.26176](https://arxiv.org/html/2609.26176v2)
- [background] CipherChat (Yuan et al., ICLR 2024): ciphers (Caesar, Morse, ASCII, "SelfCipher") bypass LLM safety alignment; attack-side only — [arXiv 2308.06463](https://arxiv.org/abs/2308.06463)
- [background] ArtPrompt (Jiang et al., ACL 2024): ASCII-art masking of trigger words; attack-side; evaluates perplexity/paraphrase/retokenization defenses on attack success — [arXiv 2402.11753](https://arxiv.org/abs/2402.11753)
- [snippet, unverified] Other 2026 items surfaced but not read: "The Boy Who Cried Wolf: Adversarial Misclassification of Safe Inputs as Unsafe in Multimodal Guardrails" (arXiv 2608.01373) — adversarially induced false positives in multimodal guards; "0%, 45%, or 99%: A Guardrail's Own Share of the Refusals It Is Credited With" (arXiv 2608.08641); "Prompt Overflow" (arXiv 2605.23196) — [2608.01373](https://arxiv.org/pdf/2608.01373), [2608.08641](https://arxiv.org/pdf/2608.08641), [2605.23196](https://arxiv.org/html/2605.23196v1)

### Inferences
- Every evasion paper on injection detectors uses ASR on attacks only; therefore when a detector does NOT get evaded (e.g., a fine-tuned DeBERTa that flags all obfuscated text), it is credited as robust. The team's metric directly corrects this blind spot.
- "Unread or Unenforced?" finds little evidence that the content guards they studied are encoding-format detectors; the team's DeBERTa-v3-small finding (format triggers blanket rejection) would be a contrasting data point for small fine-tuned injection classifiers — worth stating carefully as a difference in guard type.

### Gaps
- Did not read Emoji Attack full text to confirm absence of any benign-perturbed control.
- Did not verify whether any commercial guard vendor publishes perturbed-benign FPR.

---

## Q3. Paired / contrastive evaluation precedent and application to guardrails

### Takeaway
Paired/minimal-pair evaluation is well established in NLP (contrast sets, CheckList invariance tests) and topical benign-mirror pairing exists in safety (XSTest, HaloGuard, Membrane), but pairing each attack with a benign twin carrying the *identical perturbation* has, as of Sep 2026, been done only for generative LLM refusal ("Refusing Everything Looks Safe"), not for injection detectors.

### Cited Findings
- [snippet/background] Contrast sets (Gardner et al., Findings of EMNLP 2020): perturb test instances to probe local decision boundaries, scored with a group-level consistency metric — [arXiv 2004.02709](https://arxiv.org/pdf/2004.02709)
- [background] CheckList (Ribeiro et al., ACL 2020): Minimum Functionality, INVariance, and DIRectional expectation tests, including typo/character perturbation invariance tests for classifiers — [arXiv 2005.04118](https://arxiv.org/abs/2005.04118)
- [snippet] Vamvas & Sennrich 2021, limits of minimal pairs in contrastive evaluation — [arXiv 2109.07465](https://arxiv.org/pdf/2109.07465)
- [snippet] HaloGuard 1.0 (2026) builds a 1:1 benign mirror per harmful subcategory holding topic/vocabulary fixed and flipping intent — [arXiv 2607.02079](https://arxiv.org/pdf/2607.02079)
- [snippet] Membrane (2026) synthesizes a benign counterpart per HarmBench behaviour for guard evaluation — [arXiv 2606.05743](https://arxiv.org/pdf/2606.05743)
- [verified] "Refusing Everything Looks Safe" pairs harmful/benign x plaintext/scaffold/encoded and defines the harm-gap / gap-lost metric — this is the direct conceptual precedent for the team's "credit only if benign twin passes" idea, but on LLM refusal, with no detector evaluation and no mitigation — [arXiv 2609.26176](https://arxiv.org/html/2609.26176v2)
- [verified] Its "scaffold" arm (untransformed text in the attack template) separates template effect from character effect — a design element the team should adopt or explicitly compare against (e.g., Base64/ROT13 "wrapping" conflates wrapper template with encoding) — [arXiv 2609.26176](https://arxiv.org/html/2609.26176v2)

### Inferences
- The team's per-pair metric (detection credited only when the benign twin passes) is a pair-level consistency metric in the contrast-set tradition; its novelty lies in application to injection detectors and in its exact definition, not in the paired-evaluation idea itself. 2609.26176's Delta is an aggregate rate difference, not a per-pair joint-correctness metric — this is a real but narrow distinction.

### Gaps
- Did not find any CheckList-style invariance suite published specifically for prompt-injection detectors.
- HaloGuard and Membrane details are from snippets only.

---

## Q4. Defenses: normalization/canonicalization, perplexity filters and their FP problems, adversarial training of detectors

### Takeaway
Normalization (NFKC, zero-width/tag stripping, confusable mapping) is widely recommended in practitioner tooling and appears as a deployable defense in at least one RAG benchmark, but no paper I found ablates normalization in front of an injection classifier while measuring both attack recall and perturbed-benign FPR. Perplexity filters have documented false positives on benign text. Adversarial/augmented training of detectors exists (PIDS-Bench hard negatives, HiveTraceGuard-Pro obfuscation on both labels) and shows a recall/FPR trade-off.

### Cited Findings
- [snippet] Alon & Kamfonas 2023: GPT-2 perplexity flags adversarial suffixes, but "false positives are a significant challenge" for plain perplexity filtering on diverse benign prompts; a LightGBM on perplexity + token length mitigates; human-crafted jailbreaks have low perplexity and evade — [arXiv 2308.14132](https://alphaxiv.org/abs/2308.14132)
- [snippet] Jain et al. 2023 "Baseline Defenses" windowed perplexity filter; reported benign false-positive rate of roughly 7% on AlpacaEval (as cited via secondary source) — [arXiv 2309.00614](https://arxiv.org/abs/2309.00614) (figure from secondary summary; not re-verified)
- [inference, not sourced] Perplexity filters would by construction flag Base64/ROT13/leetspeak/homoglyph benign text (high perplexity), i.e., the same over-defense the team observes; I found no paper quantifying this specifically.
- [snippet] OpenRAG-Soc / "Hidden-in-Plain-Text" (arXiv 2601.10923) evaluates Unicode normalization (NFKC, removing zero-width) as one of three deployable defenses for social-web indirect injection in RAG — [arXiv 2601.10923](https://arxiv.org/html/2601.10923v2)
- [snippet] "Reverse CAPTCHA" (arXiv 2603.00164) warns naive zero-width stripping breaks ZWJ in Indic scripts and emoji sequences; recommends targeted codepoint rules — [arXiv 2603.00164](https://arxiv.org/html/2603.00164v1)
- [snippet] Practitioner normalizers: sibyllinesoft/clean (strip zero-width, bidi overrides, NFKC, confusable mapping before classification) — [GitHub](https://github.com/sibyllinesoft/clean)
- [verified] PIDS-Bench hard-negative augmentation: curated over-defense nearly eliminated, external over-defense persists; normalization not discussed — [arXiv 2609.15017](https://arxiv.org/html/2609.15017)
- [verified] HiveTraceGuard-Pro trains with obfuscation on both labels; persistent coupling between obfuscated-harm recall and obfuscated-benign over-blocking; no inference-time normalizer — [arXiv 2609.01046](https://arxiv.org/html/2609.01046)
- [verified] PIGuard/MOF reduces trigger-word bias (lexical), not orthographic bias — [arXiv 2410.22770](https://arxiv.org/html/2410.22770v3)

### Inferences
- A controlled comparison of (i) canonicalization preprocessing, (ii) benign-twin augmentation, (iii) both, measured with paired metrics on seen vs unseen perturbation families, appears unpublished. Normalization handles zero-width / soft hyphen / homoglyph / fullwidth cleanly but cannot "undo" leetspeak reliably and does not address Base64/ROT13 unless decode-and-rescan is added; the team should expect normalization to dominate for invisible/confusable chars and augmentation to be needed for wrappers.
- HiveTraceGuard-Pro's coupling result predicts the team's augmentation will trade attack recall for benign FPR; normalization may break that coupling for the char-level families because it removes the feature rather than relearning it — a testable, novel hypothesis.

### Gaps
- No primary source found quantifying perplexity-filter FPR on encoded/obfuscated benign text.
- No paper found ablating NFKC/confusable normalization in front of an injection classifier with benign-side FPR.

---

## Q5. What remains open: novelty assessment and closest competitors

### Takeaway
The broad idea ("attack-only obfuscation evaluation hides over-refusal; restore the benign arm") was published for generative LLMs on 24 Sep 2026 (arXiv 2609.26176), and benign-obfuscation FPR + recall/FPR coupling was reported for one generative guard on 1 Sep 2026 (arXiv 2609.01046). What still appears novel is: the paired benign-twin protocol and per-pair metric applied to prompt-INJECTION detectors, a cross-guard measurement across public injection classifiers, the specific perturbation set incl. soft hyphens and Base64/ROT13 wrappers, and a controlled normalization-vs-augmentation mitigation study.

### Cited Findings (closest competitors, ranked)
1. [verified] "Refusing Everything Looks Safe" (arXiv 2609.26176, Sep 2026) — same thesis and paired harmful/benign x encoded design + harm-gap metric, but generative LLMs only, mainly homoglyphs, no detectors, no mitigation — [arXiv 2609.26176](https://arxiv.org/html/2609.26176v2)
2. [verified] PIDS-Bench (arXiv 2609.15017, Sep 2026, IEEE Access) — injection detectors incl. DeBERTa-v3 and ProtectAI/PromptGuard 2; leetspeak/homoglyph/zero-width obfuscation but attack-only ("benign FPR is undefined"); benign-side structural shift FPR 0.81 for DeBERTa-v3-FT; hard-negative augmentation; lists generalization to unseen obfuscations as open — [arXiv 2609.15017](https://arxiv.org/html/2609.15017)
3. [verified] HiveTraceGuard-Pro (arXiv 2609.01046, Sep 2026) — obfuscated benign FPR (0.139 vs 0.016 clean) for a 0.6B generative guard, training on obfuscation for both labels, coupling trade-off; no normalizer, single model, not a cross-guard study — [arXiv 2609.01046](https://arxiv.org/html/2609.01046)
4. [verified] InjecGuard/PIGuard + NotInject (arXiv 2410.22770; ACL 2025) — owns "over-defense" for injection detectors, lexical trigger words only — [ACL 2025](https://aclanthology.org/2025.acl-long.1468)
5. [verified] Hackett et al. (arXiv 2504.11168; LLMSEC 2025) — the char-injection evasion baseline across 6 injection/jailbreak guards; attack-only ASR — [arXiv 2504.11168](https://arxiv.org/html/2504.11168v2)
6. [verified, non-peer-reviewed] HF blog "Safe ASR" on content guards — perturbed benign over-blocking for 3 content-safety guards (max 15-25%) — [HF blog](https://huggingface.co/blog/kalyan-ks/llm-guardrail-models-less-robust)
7. [verified] "Unread or Unenforced?" (arXiv 2609.26178) — encoded-input mechanistic analysis of content guards; same group as #1 — [arXiv 2609.26178](https://arxiv.org/abs/2609.26178)

### Inferences (novelty map for the planned contribution)
- Paired-perturbation protocol (benign twin per attack, same perturbation): PARTIALLY PRE-EMPTED in concept by 2609.26176 (LLMs) and loosely by HiveTraceGuard-Pro (obfuscation on both labels). Still NOVEL for injection detectors and with exact per-attack twinning. Must cite 2609.26176 prominently and position as "the detector analogue + per-pair metric".
- Metric crediting detection only if benign twin passes: NOT found in prior work for guards; 2609.26176's Delta / gap-lost is the nearest (aggregate difference, not per-pair joint correctness). Contrast-set consistency (Gardner et al. 2020) is the methodological ancestor. Moderate novelty; reviewers will see it as a natural metric, so its value must be shown empirically (rank reversals across guards vs ASR/recall-only rankings).
- Cross-guard measurement study on injection detectors with perturbed benign: appears NOVEL (no paper found covering ProtectAI v1/v2, Prompt Guard 1/2, PIGuard, Deepset, etc. with benign-twin FPR). Strongest contribution if it shows that guards reported as "robust" in Hackett-style or PIDS-style attack-only evaluations are format-rejecters.
- Mitigation: benign-twin augmentation alone is PARTIALLY PRE-EMPTED (HiveTraceGuard-Pro; PIDS-Bench hard negatives) and known to show a recall/FPR coupling; canonicalization preprocessing is folk practice but UNEVALUATED in this paired setting. A controlled ablation (normalize vs augment vs both; seen vs held-out perturbation families; decode-and-rescan for Base64/ROT13) remains open and would be the most defensible novel mitigation claim.
- Specific perturbations: soft hyphen (U+00AD) and ROT13 wrapping were not in any detector paper I checked (Hackett uses zero-width, homoglyph, "numbers", tags, emoji, etc.; PIDS-Bench uses leet/homoglyph/zero-width; 2609.26176 lacks leet/ROT13). Minor novelty only.
- Timing risk: three directly relevant preprints appeared 1-24 Sep 2026; the team should move quickly and position against them explicitly. A wrapper-vs-character decomposition ("scaffold" arm per 2609.26176) is expected by reviewers for Base64/ROT13 wrappers.
- The team's own numbers (73-98% FPR) are much larger than HiveTraceGuard-Pro's 13.9% augmented-benign FPR and the HF blog's 15-25% Safe ASR on content guards; plausible explanation (inference): small discriminative injection classifiers trained on attack-heavy data learn "out-of-distribution format => injection", while generative/content guards with broader pretraining-aligned data do not. Should be tested across guards rather than asserted.

### Gaps
- Search was not exhaustive (~18 search/fetch calls); there may be additional 2026 preprints (the area is moving weekly). Recommend a final arXiv check for "benign twin", "paired perturbation", "format bias", "obfuscation over-defense" before submission.
- Did not confirm whether PIDS-Bench code/data includes benign obfuscated samples that could be reused.
- Fairoze et al., "Bypassing Prompt Guards in Production with Controlled-Release Prompting" (USENIX Security 2026) surfaced only as a bibliography entry; method and whether benign controls are used were not verified — [arXiv 2609.26178 search result context](https://arxiv.org/pdf/2609.26178)
