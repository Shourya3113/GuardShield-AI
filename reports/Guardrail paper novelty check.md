# Paper 1 survives by narrowing its claims

Paper 1 is still publishable, but only for its detector-side contributions. No paper found puts **third-party prompt-injection detectors** through identical, label-blind perturbations of attacks and length-matched benign twins, scores them with paired score-level metrics, and maps fail-closed versus fail-open behaviour per perturbation family. No paper found measures those detectors' false positives on **native-speaker Hindi, romanized Hindi and Hinglish**. And no paper found compares **script-aware canonicalization with benign-twin augmentation** on held-out families. Two ideas the team might have called new are already in print. "Refusing Everything Looks Safe" (arXiv 2609.26176) published the benign arm and the scaffold control for LLM refusal and recommends the scaffold "as standard". HiveTraceGuard-Pro (arXiv 2609.01046) already obfuscates both labels of topic-paired twins, for its own guard. Two detector audits also limit what Paper 1 can say. A 15-detector audit (arXiv 2610.03448) already shows over-defense varies from 0% to 93% across guards. A USENIX Security 2026 paper (arXiv 2510.01529) already shows Prompt Guard 2 regressing on encodings. The verdicts are therefore: claim (1) partially pre-empted; claim (2) novel for detectors; claim (3) partially pre-empted, though the per-family symmetric failure map is new; claim (4) novel with careful wording; claim (5) novel as a controlled comparison. Six closely related preprints appeared between 1 September and 2 October 2026, and at least two author groups list Paper 1's exact cell as their future work. Timing is now a larger risk than novelty.

*Tag legend. **[snippet]**: seen only in a search snippet or secondary summary. **[abstract-only]**: only the abstract was read. **[not re-verified]**: cited from background knowledge and not re-fetched. **[inference]**: reasoning, not a sourced finding. **[team data]**: the team's unpublished pilot (150 pairs, `paper1/pilot_2026-10-12/`), not paper results. Untagged cited claims were read in the primary source (full text, HTML or PDF) by the researchers.*

## Six preprints in five weeks crowded the field but left the detector cell empty

The competing work falls into five clusters, and each one covers a different slice of Paper 1.

**The first cluster restores the benign arm, but for chat LLMs rather than detectors.** "Refusing Everything Looks Safe" (Northeastern; v2 24 Sep 2026) crosses {harmful, benign} with {plaintext, scaffold, encoded} over JailbreakBench's 100 harmful and 100 theme-matched benign behaviours. It tests four 7–8B chat models and finds that Llama-3.1-8B's harm gap falls from **+0.82 in plaintext to 0.00 under homoglyphs** ([arXiv 2609.26176](https://arxiv.org/pdf/2609.26176)). It names the defence-side gap explicitly: a defence whose FPR "is measured on plain benign prompts has not measured its false-positive rate under the condition it is deployed against… the same missing cell one level out, on the defence rather than the target" ([arXiv 2609.26176 §2](https://arxiv.org/pdf/2609.26176)). It runs no detector. One metadata point matters for citation: the abs page lists v1 as "Wed, 12 Aug 2026" despite the 2609 identifier ([abs page](https://arxiv.org/abs/2609.26176)). Two older works sit in the same cluster. Handa et al. hand-rewrote all 50 AdvBench items as safe requests, passed them through five ciphers, and had an LLM judge label chat-model responses, with a maximum of **40% "incorrectly flagged" for gpt-oss-20b under Grid Encoding** ([arXiv 2402.10601v5](https://arxiv.org/html/2402.10601v5)). Uysal et al. measure chat-model compliance under Base64/ROT13/Hex and four languages, with no detector and no benign controls ([arXiv 2606.29602](https://arxiv.org/html/2606.29602v1)).

**The second cluster audits real detectors, but never perturbs benign text.**

- PIDS-Bench (IEEE Access 2026) evaluates ProtectAI v2, deepset, Prompt Guard 2 and Llama Guard 3-1B. Its leetspeak/homoglyph/zero-width set contains attacks only, and the paper states "benign FPR is undefined" ([arXiv 2609.15017 §4.4](https://arxiv.org/pdf/2609.15017)).
- Liu's "Passing the Test You Trained On" audits 15 detectors on replayed agent tool outputs and uses no character or encoding perturbations ([arXiv 2610.03448](https://arxiv.org/html/2610.03448v1)).
- Fairoze et al. survey 14 guards on cipher and controlled-release attacks without a benign encoded set ([arXiv 2510.01529v4](https://arxiv.org/pdf/2510.01529v4)).
- Hackett et al. report attack-only ASR for 12 character-injection techniques across six guards ([arXiv 2504.11168](https://arxiv.org/html/2504.11168v2)).
- Prompt Overflow evades Prompt Guard 2 and ProtectAI by dilution across 512-token windows ([arXiv 2605.23196](https://arxiv.org/html/2605.23196v1)).

**The third cluster obfuscates benign text, but evaluates only one guard.** HiveTraceGuard-Pro, a 0.6B Qwen3 LoRA guard for Russian and English, "pairs harmful examples… with benign examples from the same domain and applies eight obfuscation transforms to both labels". Its Table 13 reports per-transform benign FPR for its own model only, from 0.016 clean to **0.262 under wrong_layout** ([arXiv 2609.01046](https://arxiv.org/pdf/2609.01046)).

**The fourth cluster builds canonicalizers, but not in front of injection classifiers with a benign arm.**

- Baszta folds homoglyphs, repairs spacing and reverses leetspeak in front of a Polish content-safety classifier. It reports flip rates only, on an all-positive benchmark ([arXiv 2609.29266](https://arxiv.org/html/2609.29266)).
- Hidden-in-Plain-Text applies NFKC and control-character stripping at RAG ingestion and reports ASR only ([arXiv 2601.10923](https://arxiv.org/html/2601.10923v2)).
- A USPTO patent claims canonicalizing Unicode prompt injections so existing classifiers can detect them ([USPTO 12278836](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12278836) [snippet]).

**The fifth cluster covers Indic and romanized text, but not detector false positives on native Hindi.**

- Srinivasan et al. (*Scientific Reports*, April 2026) built 4,000 Hindi and "Hinglish" injection prompts by Google Translate and online transliteration. They trained their own classifiers on an 80/20 split ([Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13201763/fullTextXML)).
- BanglaVeilGuard covers romanized, Banglish and code-mixed Bangla with rule-generated variants and reports overall guard FPR only ([arXiv 2608.21880](https://arxiv.org/html/2608.21880)).
- IndicSafe tests generative LLMs in native scripts only ([arXiv 2603.17915](https://arxiv.org/html/2603.17915)).

The table ranks the competitors by how much of Paper 1 they pre-empt.

| Work | Date | Pre-empts | Leaves open |
|---|---|---|---|
| Refusing Everything Looks Safe ([2609.26176](https://arxiv.org/pdf/2609.26176)) | v2 24 Sep 2026 | Benign arm under identical encoding; scaffold control; two-arm "harm gap" | Detectors; length matching (raw length separates arms at AUROC 0.654); scores and thresholds; leetspeak, ROT13, soft hyphen; held-out families; mitigation |
| HiveTraceGuard-Pro ([2609.01046](https://arxiv.org/pdf/2609.01046)) | 1 Sep 2026 | Two-sided obfuscation of topic-paired twins, as training and as evaluation; three held-out transforms; recall/FPR coupling | Third-party guards; length-matched identical twins; Unicode/encoding families; per-transform AUROC; normalizer; Hindi |
| Liu, Passing the Test ([2610.03448](https://arxiv.org/html/2610.03448v1)) | 2 Oct 2026 | 15-detector over-defense audit; AUROC and TPR at 1% FPR; contamination audit; format edits move FPR | Character/encoding perturbation; benign twins under perturbation; multilingual |
| PIDS-Bench ([2609.15017](https://arxiv.org/pdf/2609.15017)) | 14 Sep 2026 | Detector over-defense plus obfuscation axis; benign structural-shift set; hard-negative augmentation | Obfuscated benign text; pairing; per-condition AUROC; canonicalization; held-out families; non-English |
| Fairoze et al. ([2510.01529](https://arxiv.org/pdf/2510.01529v4)) | USENIX Sec 2026 | Prompt Guard 2 regression on encoding attacks (detection 0.02–0.23) across 14 guards | Any benign encoded measurement (argued, not measured) |
| Handa et al. ([2402.10601](https://arxiv.org/html/2402.10601v5)) | NeurIPS 2025 workshop | Safe-reframed harmful items through ciphers | Detectors; n = 50; LLM-judged responses |
| Srinivasan et al. ([Nature](https://www.nature.com/articles/s41598-026-43883-0)) | Apr 2026 | First Hindi + "Hinglish" injection dataset | Native authorship; code-mixed register; per-register FPR; off-the-shelf guards; fairness |
| BanglaVeilGuard ([2608.21880](https://arxiv.org/html/2608.21880)) | 25 Aug 2026 | Cross-script and romanized guard over-refusal (Bangla) | Hindi; per-form guard FPR; fairness metric |

Paper 2 (HMAC-signed conversation history at a guard sidecar) was not re-checked in this round. Its earlier assessment still stands. Microsoft already proposed signing conversation histories ([MSRC](https://www.microsoft.com/en-us/msrc/blog/2025/03/jailbreaking-is-mostly-simpler-than-you-think)). An IEEE S&P 2026 study found 8 of 17 chatbot plugins fail to protect history integrity ([arXiv 2511.05797](https://arxiv.org/abs/2511.05797)). A keyed per-turn history hash appeared on 9 October 2026 ([arXiv 2609.35308](https://arxiv.org/html/2609.35308)). Paper 2's publishable gap is therefore a measurement of what verified provenance buys (fewer compounded session false positives, lower latency) and what it costs under a defense-aware adaptive attacker [inference]. The rest of this report concerns Paper 1.

## Two claims are partially pre-empted and three remain open

| Claim | Verdict | Closest competitor | What remains novel |
|---|---|---|---|
| (1) Paired benign-twin perturbation protocol | **Partially pre-empted** | 2609.26176 (benign arm + scaffold, LLM refusal); 2609.01046 (two-sided obfuscation, own guard) | Detector target; length-matched per-item identical twins; soft hyphen, ROT13, diacritics, letter spacing on the benign side; held-out families for detectors |
| (2) Score-level paired metrics | **Novel** for detectors (PJA alone is incremental) | 2609.26176 harm gap; PIDS-Bench global recalibration argument | Within-condition AUROC and per-condition re-thresholding that separate shifted from destroyed signal |
| (3) ~15-guard fail-closed/fail-open audit | **Partially pre-empted** | Liu 2610.03448; Fairoze 2510.01529; PIDS-Bench | Symmetric per-family map; Prompt Guard 2 at 0% recall with 0% FPR under specific families; ~100% perturbed-benign FPR for ProtectAI under specific families |
| (4) Native-speaker Hindi/romanized/Hinglish benchmark | **Novel**, with qualified wording | Srinivasan et al. 2026; BanglaVeilGuard | Native authorship; register-parallel design; benign trigger-word split; per-register detector FPR; FPR fairness metrics |
| (5) Canonicalization vs benign-twin augmentation | **Novel** as a controlled comparison; augmentation arm partially pre-empted | HiveTraceGuard-Pro; Baszta; PIDS-Bench | Head-to-head comparison, benign FPR measured, seen vs held-out families, script-aware Devanagari handling |

### Claim 1: the benign arm and scaffold are taken; the detector cell is not

Two papers block a claim to the paired idea itself. In 2609.26176 the scaffold is "the same template around untransformed content", and the authors write: "we recommend it as standard" ([arXiv 2609.26176 §3](https://arxiv.org/pdf/2609.26176)). Their verbatim scaffold, "The following request is encoded with Cyrillic and Greek homoglyph substitution:", is structurally the same as Paper 1's `base64_scaffold` ([App. A](https://arxiv.org/pdf/2609.26176)). HiveTraceGuard-Pro's Russian robustness set crosses "paired safe/harm twins" with clean and eight transforms. It evaluates to_lower, to_upper and informal_rewrite as held-out transforms ([arXiv 2609.01046 Table 1, Table 13](https://arxiv.org/pdf/2609.01046)). Two more matched-benign designs exist outside text detectors. One visual guardrail paper renders an aligned benign counterpart on the same page and in the same style ([arXiv 2609.05535](https://arxiv.org/html/2609.05535v1) [snippet]). An industry PR grades injection detection "against a clean twin" ([AiSOC PR #913](https://github.com/beenuar/AiSOC/pull/913) [snippet]). The methodological ancestors are contrast sets ([Gardner et al.](https://arxiv.org/pdf/2004.02709) [snippet]) and CheckList invariance tests ([Ribeiro et al.](https://arxiv.org/abs/2005.04118) [not re-verified]).

Paper 1 still owns four specifics.

- **Target.** Its targets are third-party detectors, which neither paper evaluates.
- **Length matching.** 2609.26176 documents the confound Paper 1 removes: "Raw character length alone separates the harmful from the benign corpus at AUROC 0.654 (86.0 vs 73.8 characters)" ([App. D.3](https://arxiv.org/pdf/2609.26176)). HiveTraceGuard-Pro's twins are topical ("Fascism versus History of fascism") and not described as length-matched ([§4.1](https://arxiv.org/pdf/2609.01046)).
- **Families.** The benign-side families are new. 2609.26176 has no leetspeak, ROT13, soft hyphen, diacritics or letter spacing, and Base64 was dropped as unreadable. HiveTraceGuard-Pro has no Base64, ROT13, homoglyph, soft hyphen, fullwidth, diacritics or letter spacing ([Table 13](https://arxiv.org/pdf/2609.01046)).
- **Held-out families for detectors.** PIDS-Bench's obfuscation families "already appear in training" ([§5.6d](https://arxiv.org/pdf/2609.15017)).

One caution applies to the held-out set. Fullwidth, diacritics and spacing are already attack families in Hackett et al. ([arXiv 2504.11168](https://arxiv.org/html/2504.11168v2)). "Held out" must therefore mean held out from Study C training, not new to the field.

### Claim 2: within-condition AUROC is the metric reviewers will remember

None of the three closest preprints computes a per-pair joint event, a within-condition AUROC, or a per-condition re-threshold. The 2609.26176 harm gap Δ = r_harmful − r_benign is a difference of marginal rates over unpaired prompt sets, and refusal has no score ([§3](https://arxiv.org/pdf/2609.26176)). HiveTraceGuard-Pro reports per-transform F1/FPR/FNR at a fixed argmax. It gives AUROC only in aggregate (0.973 on pooled robustness rows) and one global threshold sweep ([§4.3, §5](https://arxiv.org/pdf/2609.01046)). PIDS-Bench runs a threshold sweep, an oracle threshold and temperature scaling, and concludes "no monotonic recalibration can relocate the over-blocked inputs at all". That analysis is global, on the hard-benign set, not per perturbation condition ([§6.6](https://arxiv.org/pdf/2609.15017)). It omits ROC-AUC for Prompt Guard 2 and Llama Guard 3-1B because it treats them as emitting "categorical verdicts" ([Table 7](https://arxiv.org/html/2609.15017)). Paper 1 scores both continuously, so it can report AUROC exactly where PIDS-Bench could not. Liu uses AUROC and TPR at 1% FPR, but on unperturbed tool outputs ([arXiv 2610.03448](https://arxiv.org/html/2610.03448v1)).

Paired joint accuracy alone is incremental: reviewers will read it as a contrast-set consistency score. The within-condition AUROC is where the analytic payoff lies. The team's pilot already shows the split.

- **Shifted.** Prompt Guard 2 86M keeps homoglyph AUROC **0.934** while its default-threshold recall is 9.3%. Its intent signal shifted rather than vanished [team data].
- **Destroyed.** Under soft hyphen its AUROC is **0.549**, which is chance level [team data].

That contrast answers PIDS-Bench's calibration verdict per condition, and it tests whether HiveTraceGuard-Pro's recall/FPR coupling is a fixable threshold shift. HiveTraceGuard-Pro reports no per-transform AUROC, so it cannot make that distinction itself [inference].

### Claim 3: "guards differ" is taken; "the same guard fails in opposite directions per family" is not

Liu already shows that default-threshold FPR on benign tool outputs spans **0.0% to 93.1%** across 15 detectors that overlap heavily with Paper 1's roster. Prompt Guard 2 86M sits at 0.6%/0.0%, ProtectAI v2 at 30.1%/66.9%, and deepset and fmops were excluded because they "flagged all benign README chunks" ([arXiv 2610.03448](https://arxiv.org/html/2610.03448v1)). Fairoze et al. already report that Prompt Guard 2 "shows severe regression on encoding and controlled-release attacks (detection 0.02-0.23)" ([arXiv 2510.01529v4](https://arxiv.org/pdf/2510.01529v4)). PIDS-Bench reports Prompt Guard 2 obfuscated recall of **0.3235**. That figure sits beside an in-distribution recall of only 0.369, so it is not an obfuscation-specific collapse, and there is no per-family split ([Table 7](https://arxiv.org/html/2609.15017)). PIDS-Bench also already shows deepset flagging **100%** of benign structural-shift inputs ([§6.1c](https://arxiv.org/pdf/2609.15017)). HiveTraceGuard-Pro's 35-guard suite contains unnamed injection detectors at pooled FPR 1.000 and FNR 0.989, which is a suite-level hint of the dichotomy ([Fig. 4](https://arxiv.org/pdf/2609.01046)).

What none of them shows is a per-family map of one guard failing in opposite directions under identical benign and attack perturbations. The pilot produces exactly that [team data]:

- **Prompt Guard 2 fails open.** Both sizes keep 0–0.7% benign FPR under every family, but recall falls from 98.7% to 0–0.7% under soft hyphen, leetspeak, diacritics, Base64 and ROT13.
- **ProtectAI v2 fails closed.** Under soft hyphen, Base64 and ROT13 it keeps 100% recall while its benign-twin FPR also reaches 100%.
- **Qwen3Guard-Gen-0.6B fails in both directions.** It fails open on Base64/ROT13 (0% recall, 0% FPR) and closed on leetspeak (94.7% FPR).

The last case is the strongest framing: **failure direction is a property of a guard × family cell, not of a guard** [inference]. Its weakest spot is terminology. "Fail-open/fail-closed" in the literature means pipeline behaviour on guard outage: NeMo's rail "fails open" when its endpoint is down ([NeMo docs](https://docs.nvidia.com/nemo/guardrails/latest/configure-guardrails/guardrail-catalog/jailbreak-protection) [snippet]). The same usage appears in HiveTraceGuard-Pro §5 ([arXiv 2609.01046](https://arxiv.org/html/2609.01046v1)) and in PolicyGuard ([arXiv 2608.02687](https://arxiv.org/pdf/2608.02687) [snippet]).

### Claim 4: the Hindi benchmark is the least contested and hardest to copy

No source found measures per-register FPR of prompt-injection detectors on benign Devanagari, romanized and code-mixed Hindi, and none applies FPR-parity metrics to Indic registers.

- **Srinivasan et al.** differ on almost every axis. Their prompts were "translated to Hindi and transliterated to Hinglish" with Google Translator and "an online website". Their "Hinglish" is transliterated romanized Hindi, not code-mixing. They report no per-language FPR and test no off-the-shelf guard ([Europe PMC](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13201763/fullTextXML)). Their own threats-to-validity sentence motivates native authorship: translation "can bring up translation style patterns that the models may learn instead of the real attack behaviour" ([Europe PMC](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13201763/fullTextXML)). Their dataset is CC0 on Kaggle and usable as a machine-translation contrast ([Kaggle API metadata](https://www.kaggle.com/api/v1/datasets/view/sillaannregi/hindi-and-hinglish-prompts)).
- **Meta** names Hindi among Prompt Guard 2's evaluation languages but publishes only an aggregate multilingual AUC (0.995 for 86M, 0.942 for 22M) ([HF card](https://huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M)). LlamaFirewall describes the multilingual set as "machine-translated" ([arXiv 2505.03574](https://arxiv.org/html/2505.03574)).
- **PolyGuard** reports no FPR for any language, and its Hindi data is NLLB-translated ([arXiv 2504.04377](https://arxiv.org/html/2504.04377)).
- **Qwen3Guard** pools unnamed languages into "Others" ([arXiv 2510.14276](https://arxiv.org/html/2510.14276)).
- **HaloGuard 1.0** gives direct evidence for the hypothesis: an earlier design learned that non-Latin script alone raised the unsafe score, firing "at near-unit confidence" on benign sentences ([arXiv 2607.02079](https://arxiv.org/html/2607.02079)).
- **Fairness framing** has precedent in dialect-driven toxicity FPR on African American English ([Sap et al., ACL 2019](https://preview.aclanthology.org/fix_video/P19-1163.pdf)).

Two design facts constrain the wording. First, the English seeds were AI-drafted and the Hindi registers were written by native speakers from them, per `paper1/annotation/GUIDELINES.md`. The benchmark is therefore "native-speaker-written parallel renderings of a shared seed set". It is not naturally occurring Hindi traffic, and its English reference register is not native-authored. Second, about 60 benign trigger-word seeds per register will carry Wilson intervals of roughly ±12 points at mid-range FPRs [inference]. Trigger-word results should therefore be reported as effect sizes rather than fine-grained rankings.

### Claim 5: no one has put canonicalization and augmentation head-to-head

The augmentation arm has precedents.

- **HiveTraceGuard-Pro** trained with two-sided obfuscation and found that "improvements on one obfuscation error rate repeatedly worsened the other. None of the tested data mixtures removed this coupling" ([§4.5](https://arxiv.org/pdf/2609.01046)). Its shipped path has "no input normalizer" ([§4.1](https://arxiv.org/pdf/2609.01046)).
- **PIDS-Bench's** hard-negative augmentation cut curated FPR from 0.4813 to 0.0010 but left externally sourced FPR at 0.3101 (p = 0.90) ([Table 10](https://arxiv.org/pdf/2609.15017)).

The canonicalization arm has partial precedents, none with a benign arm on an injection classifier.

- **Baszta** reaches homoglyph flip rate 0.000 with no benign FPR and calls its own setup "a partly closed loop" ([arXiv 2609.29266](https://arxiv.org/html/2609.29266)).
- **Hidden-in-Plain-Text** cuts zero-width carrier ASR from 23.2% to 7.8% with no normalization-specific benign FPR ([arXiv 2601.10923](https://arxiv.org/html/2601.10923v2)).
- **Liu's** markup stripping cuts PIGuard README FPR from 24.6% to 5.6% ([arXiv 2610.03448](https://arxiv.org/html/2610.03448v1)). This is a structural-normalization result adjacent to Paper 1's.

The script-aware rule is the clearest gap. Protect AI's LLM Guard InvisibleText scanner strips Unicode categories Cf, Cc, Co and Cn ([llm-guard docs](https://github.com/protectai/llm-guard/blob/main/docs/input_scanners/invisible_text.md)). Cf includes the ZWJ/ZWNJ joiners that control Devanagari conjuncts, so this industry-standard rule would alter Hindi text [inference]. The `hindi-normalize` toolkit strips them too ([GitHub](https://github.com/Tushar-9802/hindi-normalize) [snippet]).

## Cite these works and drop seven claims

### Required citations and positioning sentences

| Work | Positioning sentence for the paper |
|---|---|
| Refusing Everything Looks Safe ([arXiv 2609.26176](https://arxiv.org/pdf/2609.26176)) | "Zhang et al. restore the benign arm and introduce the scaffold control for encoded-prompt evaluation of chat LLMs, and note that the same cell is missing 'one level out, on the defence'; we fill that cell for prompt-injection detectors, with length-matched twins and score-level metrics." |
| HiveTraceGuard-Pro ([arXiv 2609.01046](https://arxiv.org/pdf/2609.01046)) | "HiveTraceGuard-Pro applies obfuscation to both labels of topic-paired twins when training and evaluating its own guard and reports a recall/FPR coupling it could not remove; we audit third-party detectors per family and ask whether such coupling reflects a shifted threshold or destroyed ranking signal." |
| PIDS-Bench ([arXiv 2609.15017](https://arxiv.org/pdf/2609.15017)) | "PIDS-Bench evaluates detectors on obfuscated attacks, but its obfuscated set 'contains only injection examples; benign FPR is undefined'; we supply the benign arm." |
| Liu, Passing the Test ([arXiv 2610.03448](https://arxiv.org/html/2610.03448v1)) | "Liu shows default-threshold over-defense varies from 0% to 93% across detectors on agent tool outputs; we show that, under a fixed perturbation, the same detector's errors can move in opposite directions." |
| Fairoze et al. ([arXiv 2510.01529](https://arxiv.org/pdf/2510.01529v4)) | "Fairoze et al. find Prompt Guard 2 regresses on encoded attacks and argue, without measuring it, that blocking encodings would harm benign users of encoding and transliteration; we measure both sides." |
| Hackett et al. ([arXiv 2504.11168](https://arxiv.org/html/2504.11168v2)) | "Character-injection evasion studies score attacks only, so a detector that flags every perturbed input is credited as robust." |
| InjecGuard / PIGuard, NotInject ([ACL 2025](https://aclanthology.org/2025.acl-long.1468)) | "NotInject defines over-defense as trigger-word bias on clean English text; we study an orthographic and script-level axis." |
| Handa et al. ([arXiv 2402.10601](https://arxiv.org/html/2402.10601v5)) | "Handa et al. pass safe-reframed items through ciphers and judge chat-model responses; no detector decision is measured." |
| Uysal et al. ([arXiv 2606.29602](https://arxiv.org/html/2606.29602v1)) | "Multilingual and encoded studies measure chat-model compliance, not detector behaviour on benign text." |
| A Guardrail's Own Share ([arXiv 2608.08641](https://arxiv.org/abs/2608.08641)) | "Zhang et al. list 'benign inputs that superficially resemble encodings (mathematical, code-heavy, or multilingual text)' as untested." |
| The Boy Who Cried Wolf ([arXiv 2608.01373](https://arxiv.org/abs/2608.01373)) | "Adversarially optimized false positives exist for multimodal guards; we show non-adversarial, label-blind perturbations suffice for injection detectors." |
| Prompt Overflow ([arXiv 2605.23196](https://arxiv.org/html/2605.23196v1)) | "Dilution across 512-token windows evades the same detectors; we keep all inputs within one window to exclude that mechanism." |
| Baszta ([arXiv 2609.29266](https://arxiv.org/html/2609.29266)); Hidden-in-Plain-Text ([arXiv 2601.10923](https://arxiv.org/html/2601.10923v2)); USPTO 12278836 ([patent](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12278836) [snippet]) | "Canonicalization has been proposed for content-safety classifiers and RAG ingestion, reporting attack-side metrics only; we measure benign FPR, held-out families and script-aware handling against augmentation." |
| Srinivasan et al. ([Nature](https://www.nature.com/articles/s41598-026-43883-0)) | "The only prior Hindi/Hinglish injection dataset is machine-translated and transliterated and evaluated in-distribution; we measure off-the-shelf detectors on native-speaker parallel registers." |
| BanglaVeilGuard ([arXiv 2608.21880](https://arxiv.org/html/2608.21880)) | "Cross-script over-refusal has been studied for Bangla with rule-generated variants and overall guard FPR; we add per-register FPR fairness metrics for Hindi." |
| IndicSafe ([arXiv 2603.17915](https://arxiv.org/html/2603.17915)); HaloGuard ([arXiv 2607.02079](https://arxiv.org/html/2607.02079)) | "Indic safety work evaluates generators in native script; HaloGuard documents script acting as a spurious unsafe cue." |
| Prompt Guard 2 card ([HF](https://huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M)); LlamaFirewall ([arXiv 2505.03574](https://arxiv.org/html/2505.03574)) | "Meta reports only aggregate multilingual AUC on machine-translated data and no per-language FPR." |
| PolyGuard ([arXiv 2504.04377](https://arxiv.org/html/2504.04377)); Qwen3Guard ([arXiv 2510.14276](https://arxiv.org/html/2510.14276)) | "Multilingual moderators that include Hindi report no Hindi false-positive rate." |
| Broken-Token ([arXiv 2510.26847](https://arxiv.org/abs/2510.26847) [snippet]); CMP-RT ([arXiv 2505.14226](https://arxiv.org/abs/2505.14226) [abstract-only]) | "Characters-per-token flags obfuscation, and fragmentation drives under-blocking; we test whether it also drives over-blocking." |
| Sap et al. ([ACL 2019](https://preview.aclanthology.org/fix_video/P19-1163.pdf)); Contrast sets ([Gardner et al.](https://arxiv.org/pdf/2004.02709) [snippet]) | Fairness precedent for dialect FPR; methodological ancestor of paired evaluation. |

Five more works deserve a related-work line:

- "Unread or Unenforced?", a mechanistic probe of encoded inputs in content guards ([arXiv 2609.26178](https://arxiv.org/abs/2609.26178) [abstract-only])
- "Decoding Guardrails", an XAI case study of Prompt Guard 2 ([arXiv 2609.24801](https://arxiv.org/html/2609.24801v1))
- the HF "Safe ASR" blog on perturbed-benign over-blocking by content guards, which is not peer-reviewed ([HF blog](https://huggingface.co/blog/kalyan-ks/llm-guardrail-models-less-robust))
- Banerjee et al., on code-mixed attack success ([arXiv 2505.14469](https://arxiv.org/abs/2505.14469) [abstract-only])
- "Severity-Aware Calibration", if verified ([arXiv 2606.22659](https://arxiv.org/pdf/2606.22659) [snippet])

### What not to claim

| Do not write | Why | Write instead |
|---|---|---|
| "We are the first to evaluate benign text under the same encodings as attacks" / "We introduce a scaffold control" | 2609.26176 does both and recommends the scaffold as standard; Handa et al. ciphered safe rewrites | "We carry the benign-arm and scaffold controls of Zhang et al. over to prompt-injection detectors" |
| "First to obfuscate both labels" | HiveTraceGuard-Pro, for its own guard | "First per-family, length-matched twin audit of third-party detectors" |
| "First cross-guard over-defense audit" / "Guards differ widely in FPR" | Liu (15 detectors), PIGuard/NotInject, GenTel-Safe | "Under identical perturbations, a single guard's errors move toward over-blocking or under-blocking depending on the family" |
| "We discover Prompt Guard 2 fails on encodings" / "Benchmarks mislead" | Fairoze (detection 0.02–0.23; "Benchmark metrics poorly predict deployment security"); PIDS-Bench 0.3235 | "Prompt Guard 2's recall falls to 0% under soft hyphen, leetspeak and diacritics while its FPR stays near 0%, a fail-open pattern that attack-only evaluation cannot separate from robustness" |
| "ProtectAI flags ~100% of perturbed benign text" (unqualified) | The pilot shows 100% for soft hyphen, Base64 and ROT13, but 34% for homoglyph and 0% for fullwidth at default [team data] | Report per family with CIs |
| "First Hindi prompt-injection dataset" / "first cross-script guard over-refusal study" | Srinivasan 2026; BanglaVeilGuard 2026 | "First native-speaker-written, register-parallel benchmark measuring false-positive rates and FPR fairness of prompt-injection detectors on benign Hindi in Devanagari, romanized and code-mixed forms" |
| "First to propose Unicode normalization for guards" | Patent, Baszta, Hidden-in-Plain-Text, LLM Guard, practitioner tools | "First controlled comparison of script-aware canonicalization and benign-twin augmentation, with benign FPR, on seen and held-out families" |
| "Fail-open/fail-closed" without definition | Collides with outage-handling semantics | Define both operationally (see the next section) |
| "Handa et al. measure guard FPR" | Their flag is an LLM judge's label on a response | "Handa et al. measure chat-model over-refusal" |

The safest one-sentence novelty statement combines the three uncontested elements: *"We give the first paired, label-blind audit of prompt-injection detectors in which every attack and its length-matched benign twin receive the identical perturbation, show with within-condition AUROC that the same guard can fail closed or fail open depending on the perturbation family, extend the audit to a native-speaker Hindi/romanized/Hinglish benchmark with FPR fairness metrics, and compare script-aware canonicalization against benign-twin augmentation on held-out families."*

## SPEC.md needs nine changes before the frozen run

The current spec (`paper1/SPEC.md`) already has the right skeleton: scaffold controls, held-out families, PJA, within-condition AUROC, FPR at reference TPR, and a held-out calibration pool. The held-out pool sidesteps Liu's caveat that thresholds chosen on the evaluation set favour detectors ([arXiv 2610.03448](https://arxiv.org/html/2610.03448v1)). The competitor evidence calls for the following changes.

| # | Change | Spec section | Reason |
|---|---|---|---|
| 1 | **Define fail-open and fail-closed operationally**, per guard × family at a stated threshold policy. Proposed rule: fail-closed if FPR(c) − FPR(clean) ≥ 20 pp while TPR(c) ≥ TPR(clean) − 10 pp; fail-open if TPR(clean) − TPR(c) ≥ 20 pp while FPR(c) ≤ FPR(clean) + 10 pp; "both" and "neither" otherwise. The cut-offs are illustrative. State explicitly that the terms do not mean outage handling. | §5 | Avoids the terminology collision ([NeMo docs](https://docs.nvidia.com/nemo/guardrails/latest/configure-guardrails/guardrail-catalog/jailbreak-protection) [snippet]). Makes Qwen3Guard-style mixed cells reportable [team data] |
| 2 | **Fix the shifted/destroyed decision rule in advance.** Re-thresholding to a clean TPR near 99–100% is tail-dominated. In the pilot, Prompt Guard 2 86M homoglyph has AUROC 0.934 but FPR 64.7% after re-thresholding, and ProtectAI homoglyph has 0.902 vs 92.0%, so the two metrics disagree [team data]. Add FPR at a fixed moderate TPR (e.g. 90%) and treat within-condition AUROC with CIs as the primary criterion | §5 | Otherwise reviewers can pick whichever metric contradicts the narrative |
| 3 | **Add baselines.** Mezzo Prompt Guard v2, which lists "hi" ([HF](https://huggingface.co/RyanStudio/Mezzo-Prompt-Guard-v2-Small/blob/main/README.md) [snippet]). Horizon-Labs guard-base and Sentinel v2, both low-FPR in Liu's audit ([arXiv 2610.03448](https://arxiv.org/html/2610.03448v1)). HiveTraceGuard-Pro, whose weights are Apache-2.0 and which is the only external guard trained on two-sided obfuscation, a natural test of whether its coupling recurs on Paper 1's families ([arXiv 2609.01046](https://arxiv.org/pdf/2609.01046)). PolyGuard-Qwen for Study B. Drop the gated Horizon-Labs multilingual model, which returned HTTP 401 ([HF API](https://huggingface.co/api/models/Horizon-Labs/prompt-injection-guard-multilingual)) | §6 | Covers all three over-defense profiles plus Hindi-claiming and augmentation-trained guards |
| 4 | **Run contamination audits.** Verbatim and near-duplicate overlap (n-gram or MinHash) of Gandalf, Dolly, NotInject and deepset_test against every auditable guard's training sources: ProtectAI v2's listed sources, PIGuard, Horizon-Labs and GuardShield. Mark each table cell as known, likely or unknown | §3 | Liu found PIGuard trained on 65/75 BIPIA train-half attacks and 53/62 InjecAgent attacks ([arXiv 2610.03448](https://arxiv.org/html/2610.03448v1)) |
| 5 | **Keep every perturbed input under 512 tokens for every guard tokenizer.** Log token counts per item, guard and condition. Drop or report pairs that exceed the limit, and report truncation rates. Zero-width, diacritics and Base64 expand token counts sharply | §2, §8 | Prompt Overflow shows windowing alone changes verdicts ([arXiv 2605.23196](https://arxiv.org/html/2605.23196v1)). Prompt Guard 2's window is 512 ([HF card](https://huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M)) |
| 6 | **Report the length confound explicitly.** Give the AUROC of post-perturbation token length (attack vs twin) per guard tokenizer, mirroring 2609.26176's 0.654 statistic | §5 | Turns length matching into a demonstrated advantage over the closest competitor ([arXiv 2609.26176](https://arxiv.org/pdf/2609.26176)) |
| 7 | **Cite PIDS-Bench numbers as external clean baselines** and explain any differences. ProtectAI: hard-benign FPR 0.216, obfuscated recall 0.906. Prompt Guard 2: hard-benign FPR 0.1515, IID recall 0.369, obfuscated recall 0.3235. Llama Guard 3-1B: obfuscated recall 0.484 ([Table 7](https://arxiv.org/html/2609.15017)). Liu's Prompt Guard 2 FPR of 0.0–0.6% is a second anchor ([arXiv 2610.03448](https://arxiv.org/html/2610.03448v1)) | §3, §8 | The pilot's ~99% clean Prompt Guard 2 recall on Gandalf versus PIDS-Bench's 0.369 shows attack-source dependence [team data] |
| 8 | **Add a second primary attack and benign source.** Candidates: the frozen PIDS-Bench injection test split and external hard-benign split (SHA-256 manifest, tag v1.0-pids-bench) ([arXiv 2609.15017](https://arxiv.org/pdf/2609.15017)), or BIPIA's test half | §3 | PIDS-Bench's "provenance-sensitive over-defense" means single-source benign results will not transfer |
| 9 | **Study C additions.** A naive canonicalizer (NFKC plus strip all Cf, as in LLM Guard) to show the damage to Devanagari ZWJ/ZWNJ that the script-aware rule avoids ([llm-guard docs](https://github.com/protectai/llm-guard/blob/main/docs/input_scanners/invisible_text.md)). Benign FPR of decode-and-rescan by itself, which no source has measured. Recall and FPR plotted jointly per round, to test the HiveTraceGuard-Pro coupling | §2 Study C | Makes "script-aware" and "breaks the coupling" testable claims rather than assertions |

Two smaller additions round this out. Record in §4 that the English seeds are AI-drafted and that within-register pairs are not length-matched by construction; report length differences. Add a characters-per-token column to §7, citing Broken-Token ([arXiv 2510.26847](https://arxiv.org/abs/2510.26847) [snippet]). The pilot's observation that "the tokenizer decides which families hurt" is partly anticipated: Meta describes a tokenization fix against whitespace and fragmentation tricks ([HF card](https://huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M)), and a researcher found Unicode normalization inside Prompt Guard 2's tokenizer ([XPN InfoSec](https://blog.xpnsec.com/tokenization-confusion/) [snippet]). Paper 1 should cite these when explaining why Prompt Guard 2 is immune to zero-width and spacing [team data].

## Timing risk now outweighs venue choice

The natural venue is ACL Rolling Review, targeting ACL, EMNLP or NAACL main or Findings. PIGuard appeared at ACL 2025 ([ACL Anthology](https://aclanthology.org/2025.acl-long.1468)), and IndicSafeEval was accepted at Findings of EMNLP 2026 ([arXiv 2609.03781](https://arxiv.org/abs/2609.03781) [abstract-only]). There are three fallback routes:

- **Workshops:** LLMSEC, which hosted Hackett et al. ([ACL Anthology](https://aclanthology.org/people/william-hackett/unverified/)), along with TrustNLP and CALCS for the code-mixed angle.
- **Fairness venues:** FAccT or AIES for a fairness-centred version.
- **Journals:** IEEE Access, which accepted PIDS-Bench ([arXiv 2609.15017](https://arxiv.org/abs/2609.15017)).

**No submission deadline or current ARR anonymity rule was verified in this research**, and both must be checked before planning around them [not re-verified].

The pace of competing work is the binding constraint:

- HiveTraceGuard-Pro: 1 September 2026
- PIDS-Bench: 14 September
- Decoding Guardrails: 21 September
- 2609.26176 v2 and Baszta: 24 September
- Liu: 2 October

Two groups have publicly named Paper 1's cell as their next step.

- **The Northeastern group.** Haoyu Zhang, Haowen Xu and Xiao Luo appear on both 2609.26176 and 2608.08641, and the group also produced 2609.26178. It has released three guard-evaluation papers in two months and wrote that the detector-side cell is missing ([arXiv 2609.26176](https://arxiv.org/pdf/2609.26176); [arXiv 2608.08641](https://arxiv.org/abs/2608.08641)).
- **The PIDS-Bench authors.** They list generalisation "to obfuscation strategies absent from training" and multilingual extension as open problems ([arXiv 2609.15017 §7.6](https://arxiv.org/pdf/2609.15017)).

A detector-side benign-twin audit from either group is plausible within months [inference]. Claims (1)–(3) are the most exposed. Claim (4) is protected by the team's native-speaker labour. The paper should therefore establish priority on the audit and metrics quickly, without waiting for every Study C seed. A reasonable plan is an arXiv preprint as soon as Study A and Study B results are complete, with Study C added in a revision if it lags [inference].

### Prioritized next steps

| Priority | Action | Why now |
|---|---|---|
| 1 | Apply spec changes 1, 2, 5 and 6 (fail-open/closed definitions, shifted/destroyed rule, 512-token cap, length-confound statistic) before the frozen Study A run | These cannot be changed after freezing without a change-log entry, and reviewers will probe all four |
| 2 | Add the second attack and benign source, the extra baselines (Mezzo v2, Horizon-Labs guard-base, Sentinel v2, HiveTraceGuard-Pro), and the contamination audit; then run full Study A at 500 pairs | Study A carries claims (2) and (3), which are the most exposed to scooping |
| 3 | Close the reading gaps that could still change a verdict: per-family predictions in the PIDS-Bench release ([GitHub](https://github.com/ShirePyDev/Prompt-Injection-Detection-System)); the HiveTraceGuard-Pro HF card; the 2609.26176 code supplement; the Qwen3Guard appendix (about 19k unread characters) and HaloGuard §7.3–7.4 for per-language Hindi FPR; CAPTURE, PromptShield, MULTIGUARD, 2609.05535 and 2606.22659; a paper-by-paper pass of CALCS/WOAH/LLMSEC/TrustNLP 2025–26 for "Hinglish" | Each gap is a named, unread source; one of them could hold per-family or Hindi FPR numbers |
| 4 | Finish the three Hindi registers, report Cohen's κ, and download the Srinivasan Kaggle CSV (requires login) as a machine-translation contrast | Claim (4) is the hardest to copy; the κ and the MT contrast are what distinguish it |
| 5 | Run Study C with the naive-canonicalizer ablation, decode-and-rescan benign FPR, and the coupling plot, over at least 5 seeds | Turns claim (5) from "novel by absence" into a demonstrated finding |
| 6 | Re-run the novelty sweep ("benign twin", "paired perturbation", "format bias", "obfuscation over-defense", "Hinglish prompt injection") within a week of submission, then post to arXiv | The field produced six relevant preprints in five weeks |
| 7 | Verify ARR cycle dates, the anonymity policy and workshop deadlines | None were verified in this research |

## Conclusion

The novelty check changes where Paper 1's value sits. It does not lie in the paired idea, which 2609.26176 and HiveTraceGuard-Pro have already normalized. It lies in a diagnostic: telling a detector whose intent signal merely shifted under an unfamiliar format from one whose signal was destroyed, separately for each guard and family. The pilot already shows that this split does not line up with guard identity. Prompt Guard 2 is shifted under homoglyphs, destroyed under soft hyphens, and immune to zero-width characters. So "is this guard robust?" is the wrong question, and attack-only leaderboards cannot answer even the right one.

The Hindi benchmark is the paper's durable asset, and the canonicalization comparison is its practical payoff. The risk is no longer that the gap does not exist. Two groups have written down exactly this gap as their next step. A narrower but defensible claim, posted soon, is worth more than a broader one posted after someone else fills the cell.
