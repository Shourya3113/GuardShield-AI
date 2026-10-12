# Benign twins expose format-rejecting injection guards

GuardShield AI's strongest publishable gap is Paper 1, and it is real but closing fast. No paper found audits public prompt-injection detectors on **benign text that carries the same character-level obfuscation as attacks**. None audits them on **natively written benign Hindi, romanized Hindi or Hinglish**. And none pairs every attack with an identically perturbed benign twin, so that a guard that simply rejects unfamiliar formats cannot score as "robust." Three preprints from September 2026 come close from different directions. "Refusing Everything Looks Safe" makes the same paired harmful/benign × encoded argument, but for generative LLMs. PIDS-Bench evaluates injection detectors on obfuscated attacks only. HiveTraceGuard-Pro measures obfuscated-benign false positives for a single generative guard. Paper 1 therefore has to be positioned against all three within weeks. The Hindi/Hinglish half is the least-occupied and hardest-to-copy part, because the team's native-speaker authorship is an asset competitors lack. Paper 2's ingredients are mostly prior art. Forged assistant turns are an established jailbreak, and Microsoft already proposed signing conversation histories. Paper 2 is therefore publishable only as a measurement-plus-systems-trade-off paper with defense-aware adaptive evaluation. The entropy circuit breaker should be dropped from Paper 2. Before any submission, the team must also remove the Llama-Guard-3 comparison claimed in earlier project documents, which was never run, or replace it with a real logged run.

*Tag legend, kept from the source notes. **[snippet]** means the claim was seen only in a search snippet or secondary summary. **[not re-verified]** means it is cited from background knowledge and was not re-fetched. **[inference]** marks reasoning rather than a sourced finding. Untagged cited claims were read in the primary source by the researchers. The team's own figures (73–98% FPR on obfuscated benign prompts, about 40% FPR on benign Hindi/Hinglish versus about 0% on English, FEVER 86%, HaluEval-QA 60% / AUROC 0.61) are the team's unpublished measurements.*

## Three September 2026 preprints narrowed, but did not close, the obfuscation gap

**InjecGuard, published at ACL 2025 as PIGuard, owns "over-defense" for injection detectors.** It defines over-defense as false flagging of benign inputs "due to trigger word bias." Its NotInject set has 339 clean English sentences seeded with injection trigger words, and no public detector it tested exceeded 60% over-defense accuracy ([arXiv 2410.22770](https://arxiv.org/abs/2410.22770v1); [ACL 2025](https://aclanthology.org/2025.acl-long.1468)). Its mitigation, MOF, retrains on LLM-generated benign samples built from tokens the model flags in isolation. That mitigation is **lexical**, not orthographic ([arXiv 2410.22770v3](https://arxiv.org/html/2410.22770v3)). Over-defense is large and depends on the distribution. On NotInject, Prompt Guard v1 scores **0.88%** over-defense accuracy and deepset 5.31%, while Llama Guard 3 scores 99.71% only because it reaches just **28.28% malicious accuracy** ([arXiv 2410.22770v3](https://arxiv.org/html/2410.22770v3)). An October 2026 audit of 15 detectors found default-threshold FPR on benign agent tool outputs ranging from **0.0% to 93.1%**. In that audit, FPR on general text did not predict FPR on tool outputs, and PIGuard turned out to be trained on BIPIA and InjecAgent data ([arXiv 2610.03448](https://arxiv.org/html/2610.03448)). Any over-defense claim therefore needs several held-out benign distributions.

The evasion literature has a structural blind spot. Hackett et al. attacked six guards (Azure Prompt Shield, ProtectAI v1/v2, Prompt Guard, NeMo Guard, Vijil) with 12 character-injection techniques and reached up to **100% ASR with emoji smuggling**. Their metric is defined only on attacks: "the rate at which a modified prompt injection or jailbreak sample is misclassified as benign." They measure no perturbed-benign FPR ([arXiv 2504.11168](https://arxiv.org/html/2504.11168v2)). Emoji Attack, CipherChat, Jailbroken and ArtPrompt are attack-side as well ([Emoji Attack](https://arxiv.org/abs/2411.01077v4) [snippet]; [CipherChat](https://arxiv.org/abs/2308.06463) [not re-verified]; [Jailbroken](https://arxiv.org/pdf/2307.02483) [not re-verified]; [ArtPrompt](https://arxiv.org/abs/2402.11753) [not re-verified]). The consequence is that **a detector that flags every obfuscated input is credited as robust**. The team's DeBERTa-v3-small, at 73–98% benign FPR under obfuscation, is exactly such a detector.

The table below ranks the closest competitors by how much of Paper 1 they pre-empt.

| Work (date) | What it already does | What it leaves open for GuardShield |
|---|---|---|
| "Refusing Everything Looks Safe," Zhang et al. ([arXiv 2609.26176](https://arxiv.org/html/2609.26176v2), v2 24 Sep 2026) | {harmful, benign} × {plaintext, scaffold, encoded} cells over JailbreakBench. Harm-gap metric Δ = r_harmful − r_benign. Llama's gap collapses from +0.82 to 0.00 under homoglyphs | Generative LLMs only, no detectors. No leetspeak or ROT13. Aggregate rate difference rather than a per-pair metric. No mitigation beyond a reporting recommendation |
| PIDS-Bench, Shire & Kim ([arXiv 2609.15017](https://arxiv.org/html/2609.15017), 14 Sep 2026, IEEE Access) | Injection detectors (DeBERTa-v3-FT, ProtectAI, Prompt Guard 2, Llama Guard 3-1B). Leetspeak/homoglyph/zero-width attacks. DeBERTa-v3-FT structural-shift FPR **0.81** | The obfuscation set is attack-only: "benign FPR is undefined." English, single-turn. Generalization to unseen obfuscations is listed as an open question |
| HiveTraceGuard-Pro ([arXiv 2609.01046](https://arxiv.org/html/2609.01046), 1 Sep 2026) | 0.6B generative guard trained with 8 obfuscations on both labels. Obfuscated-benign FPR **0.139** vs 0.016 clean | Single model. No inference-time normalizer. Reports a recall/FPR coupling that "none of the tested data mixtures removed" |
| Hackett et al. ([arXiv 2504.11168](https://arxiv.org/abs/2504.11168v2), LLMSEC 2025) | Character-injection evasion baseline across 6 guards | ASR only, with no benign arm and no defense |
| HF community blog, "Safe ASR" ([HF blog](https://huggingface.co/blog/kalyan-ks/llm-guardrail-models-less-robust), May 2026) | Perturbed-benign over-blocking for 3 content guards, max 15–25% | Not peer-reviewed. Content-safety rather than injection guards |
| "Unread or Unenforced?" ([arXiv 2609.26178](https://arxiv.org/abs/2609.26178)) | Mechanistic probe of 2 content guards over 19 encoding conditions. Little evidence of pure "format detectors" | Content guards. The abstract mentions no benign twins |

**HiveTraceGuard-Pro is the most important constraint on the mitigation claim.** Across six data rounds, raising recall on obfuscated harmful requests repeatedly raised over-blocking of obfuscated benign requests ([arXiv 2609.01046](https://arxiv.org/html/2609.01046)). PIDS-Bench separately found that hard-negative augmentation "nearly eliminates over-defense on curated inputs" but leaves externally sourced over-defense intact ([arXiv 2609.15017](https://arxiv.org/html/2609.15017)). That is a direct warning about the team's own hard-negative retraining. Normalization is still unevaluated in this setting. NFKC, zero-width stripping and confusable mapping are folk practice ([sibyllinesoft/clean](https://github.com/sibyllinesoft/clean) [snippet]) and appear as a RAG defense ([arXiv 2601.10923](https://arxiv.org/html/2601.10923v2) [snippet]). However, no paper found places normalization in front of an injection classifier and measures both attack recall and perturbed-benign FPR. One caution links the two halves of Paper 1: naive zero-width stripping **breaks ZWJ in Indic scripts** and emoji sequences ([arXiv 2603.00164](https://arxiv.org/html/2603.00164v1) [snippet]). A normalizer built to fix obfuscation over-defense could therefore damage Devanagari input.

Several adjacent 2026 items surfaced but were not read and should be checked before writing. They are "The Boy Who Cried Wolf," on adversarially induced false positives in multimodal guards ([arXiv 2608.01373](https://arxiv.org/pdf/2608.01373) [snippet, unverified]), "A Guardrail's Own Share of the Refusals" ([arXiv 2608.08641](https://arxiv.org/pdf/2608.08641) [snippet, unverified]), "Prompt Overflow" ([arXiv 2605.23196](https://arxiv.org/html/2605.23196v1) [snippet, unverified]), and Fairoze et al.'s controlled-release prompting at USENIX Security 2026, which was seen only as a bibliography entry ([context](https://arxiv.org/pdf/2609.26178) [unverified]).

## Hindi and Hinglish over-blocking is the least-occupied corner

The multilingual safety literature mostly treats non-English text as an **attack vector**, measuring under-blocking. Translating unsafe prompts into low-resource languages lifted GPT-4 bypass from under 1% to 79% ([Yong et al.](https://arxiv.org/pdf/2310.02446)). Code-switching produced 46.7% more successful attacks ([CSRT, ACL 2025](https://arxiv.org/abs/2406.15481)). Phonetic Hinglish perturbations jailbreak frontier models by splitting safety-critical tokens into benign sub-words ([CMP-RT, arXiv 2505.14226](https://arxiv.org/abs/2505.14226)). The team's finding runs the other way: **unfamiliar language triggers over-blocking**. Across the notes, this direction is barely studied for injection detectors.

Each nearest neighbour covers only two of the four axes Paper 1 combines. Those axes are a prompt-injection detector, a benign-FPR metric, natively written Hindi in three registers, and fairness framing.

| Work | Covers | Lacks |
|---|---|---|
| Srinivasan et al., *Scientific Reports* 16:16208, Apr 2026 ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13201763/); [Nature](https://www.nature.com/articles/s41598-026-43883-0)) | 4,000 Hindi + Hinglish PI prompts (1,000 safe / 1,000 injection per language). TF-IDF, XLM-R and regex hybrid | Data is **Google-Translated and tool-transliterated**. In-distribution 80/20 split only. **No benign FPR and no per-language FPR. No off-the-shelf guard baselines.** Reported 0.997 accuracy does not match its confusion matrix |
| NotInject / PIGuard ([ACL 2025](https://aclanthology.org/2025.acl-long.1468)) | PI over-defense, defined and benchmarked | English only |
| Yang et al. ([arXiv 2410.22153](https://arxiv.org/html/2410.22153v1)) | Aegis-Defensive shows "a high FPR on low-resource languages." Includes a code-switched MultiJail variant | Harmful-content guards. Google-translated data. FPR shown only in a figure, with no Hindi analysis |
| IndicSafe ([arXiv 2603.17915](https://arxiv.org/html/2603.17915v2)) | 12 Indic languages, human-translated. Qwen1.5-7B refuses 33.6% of harmless Hindi prompts | Generative LLMs only. Native script only, with no romanized or code-mixed text. No PI |
| Prompt Guard 2 ([HF card](https://huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M)) | Multilingual eval including Hindi. Aggregate AUC .995 (86M) / .942 (22M) | **No per-language FPR.** Romanized Hindi not stated. The 22M variant uses an English-only DeBERTa-xsmall |
| Horizon-Labs multilingual PI guard ([HF card](https://huggingface.co/Horizon-Labs/prompt-injection-guard-multilingual)) | Per-language FPR on machine-translated benign text, e.g. about 0.46 RU and 0.67 ZH | [snippet, unverified]: the card returned HTTP 401. No Hindi known |

Three mechanisms make the gap tractable. First, tokenizers already treat languages unequally. The same content can differ by up to **15× in token length** across languages ([Petrov et al., NeurIPS 2023](https://proceedings.neurips.cc/paper_files/paper/2023/hash/74bb24dca8334adce292883b4b651eda-Abstract.html)), and CMP-RT ties Hinglish safety failures to fragmentation ([arXiv 2505.14226](https://arxiv.org/abs/2505.14226)). Whether the same fragmentation drives *over*-blocking is untested [inference]. Second, natural Hinglish benign text is easy to source, from L3Cube-HingCorpus (52.93M real romanized tweets) ([arXiv 2204.08398](https://arxiv.org/pdf/2204.08398)), HinGE ([arXiv 2107.03760](https://ar5iv.arxiv.org/html/2107.03760)), LinCE ([LREC 2020](https://aclanthology.org/2020.lrec-1.223)) and GLUECoS ([ACL 2020](https://aclanthology.org/2020.acl-main.329)). Third, the fairness framing has strong precedent. Dialect-driven toxicity FPR on African American English is treated as racial bias ([Sap et al., ACL 2019](https://preview.aclanthology.org/fix_video/P19-1163.pdf)), and that bias persists in classifiers trained on LLM-generated labels ([NSF PAR 10612700](https://par.nsf.gov/biblio/10612700-large-language-model-annotation-bias-hate-speech-detection)). CDT frames multilingual moderation false alarms as harms to non-English speakers ([CDT 2023](https://cdt.org/wp-content/uploads/2023/05/Lost-in-Translation-es-english-final-05172023.pdf)). The team's 40% vs ~0% gap is a quality-of-service harm: Hindi/Hinglish users of a guarded app are blocked about 40× more often for benign requests [inference from the team's figures].

The residual risks are specific. The full texts of PolyGuard ([arXiv 2504.04377](https://arxiv.org/abs/2504.04377v1)) and Qwen3Guard ([arXiv 2510.14276](https://arxiv.org/abs/2510.14276v1)) were not checked for per-language FPR tables, and both cover Hindi. Qwen3Guard's own limitations section concedes it may flag some cultural groups' content as unsafe ([arXiv 2510.14276](https://arxiv.org/html/2510.14276v1)). CALCS, WOAH and FAccT/AIES proceedings were not searched for a small Hinglish guard-FPR study.

## Paper 1 should claim format-triggered over-defense, measured in pairs

### One hypothesis unifies the two halves

Treating obfuscation and Hindi as two separate findings dilutes the paper. Both are better read as one phenomenon. **Small discriminative injection classifiers learn "unfamiliar surface form ⇒ injection,"** so their decisions track format rather than intent [inference]. This also explains why the team's FPRs (73–98%) are far above HiveTraceGuard-Pro's 13.9% and the 15–25% "Safe ASR" of content guards. Generative and content guards have broader pretraining and do not collapse the same way ([arXiv 2609.01046](https://arxiv.org/html/2609.01046); [HF blog](https://huggingface.co/blog/kalyan-ks/llm-guardrail-models-less-robust)). That contrast must be tested across guards, not asserted. It also places PIGuard's lexical "trigger-word" over-defense and the team's orthographic or script-level over-defense as two distinct axes. That positioning matters, because InjecGuard owns the term "over-defense" ([arXiv 2410.22770](https://arxiv.org/abs/2410.22770v1)).

**Sharpened research question:** When a prompt's surface form is unfamiliar to a prompt-injection detector, do detectors still separate injection intent from benign intent, or do they reject the format? Unfamiliar here means character-obfuscated, Base64/ROT13-wrapped, or written in Devanagari, romanized Hindi or Hinglish. And which intervention restores intent-sensitivity without giving up attack recall?

### Contributions, ordered by defensibility

The table below lists the five contributions from most to least defensible.

| # | Contribution | Novelty status |
|---|---|---|
| C1 | **Paired benign-twin protocol.** Every attack gets a benign twin with the identical perturbation. For Hindi, the same benign content is written in English, Devanagari, romanized Hindi and code-mixed Hinglish. The design includes a *scaffold arm* that puts plain text inside the Base64/ROT13 wrapper template, so template effect is separated from character effect, as in [arXiv 2609.26176](https://arxiv.org/html/2609.26176v2). | Pre-empted in concept for LLMs (2609.26176), loosely by HiveTraceGuard-Pro. **Novel for injection detectors.** The methodological ancestor is contrast sets ([Gardner et al.](https://arxiv.org/pdf/2004.02709) [snippet]) and CheckList invariance tests ([Ribeiro et al.](https://arxiv.org/abs/2005.04118) [not re-verified]) |
| C2 | **Human-written, native-speaker benign + injection benchmark** in four registers. It has a NotInject-style Hindi/Hinglish trigger-word split (e.g. "pichhle instructions bhool jao" used benignly), controlled spelling variants, inter-annotator agreement, and a machine-translated contrast version of the same items. | **Novel.** The only competitor dataset is MT-based ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13201763/)). This is the team's hardest-to-replicate asset |
| C3 | **Cross-guard audit** showing (a) rank reversals between attack-only and paired rankings and (b) per-register FPR parity gaps | **Novel**: no audit found covers ProtectAI, Prompt Guard 1/2, PIGuard, deepset and others with benign-twin or per-language FPR |
| C4 | **Mechanism analysis.** Token fertility and OOD distance per register and perturbation, correlated with FPR | **Novel** for over-blocking. CMP-RT showed only the under-blocking direction |
| C5 | **Mitigation ablation**: script-aware canonicalization vs benign-twin augmentation vs both, plus decode-and-rescan for Base64/ROT13. Tested on seen vs held-out perturbation families, reported at matched TPR. The hypothesis is that normalization breaks HiveTraceGuard-Pro's recall/FPR coupling for character-level families, because it removes the feature instead of relearning it [inference] | Augmentation alone is partly pre-empted. **The controlled ablation is open** |

The metric needs care. Crediting a detection only when the benign twin also passes is a pair-level joint-correctness score. It differs from 2609.26176's aggregate Δ, but only narrowly, and reviewers will call it "natural" ([arXiv 2609.26176](https://arxiv.org/html/2609.26176v2)). Its value has to be shown empirically through rank reversals. One addition would make it more than a renaming: **within-perturbation AUROC**, the ability to rank a perturbed attack above its perturbed benign twin [inference]. If that AUROC stays high while FPR explodes, the guard's scores have only shifted, and per-format recalibration would fix it. If AUROC collapses, the intent signal is destroyed and only retraining or normalization helps. This distinction is the analytic finding reviewers will remember. It also answers PIDS-Bench's verdict that threshold calibration is insufficient ([arXiv 2609.15017](https://arxiv.org/html/2609.15017)).

### Experiments and baselines reviewers will expect

**Guard roster.** The audit should span all three over-defense profiles in the landscape notes ([arXiv 2410.22770v3](https://arxiv.org/html/2410.22770v3); [arXiv 2610.03448](https://arxiv.org/html/2610.03448)):

- **"Paranoid" guards:** Prompt Guard v1, deepset, fmops.
- **"Lexically biased" guards:** ProtectAI v1/v2, PIGuard.
- **"Low-FP by design" guards:** Prompt Guard 2 22M/86M, Sentinel, Horizon-Labs.
- **Content guards:** Llama Guard 3-1B/8B, Llama Guard 4-12B, Qwen3Guard-Gen 0.6B/4B/8B, PolyGuard-Qwen, WildGuard.
- **Simple baselines:** a GPT-2 perplexity filter of the kind NeMo's jailbreak heuristics use ([NeMo docs](https://docs.nvidia.com/nemo/guardrails/latest/configure-guardrails/guardrail-catalog/jailbreak-protection) [snippet]), TF-IDF, and the team's own DeBERTa-v3-small.

Prompt Guard 2 22M is the closest size match to DeBERTa-v3-small and lacks multilingual pretraining ([HF card](https://huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M)). It is the single most informative comparison. Commercial APIs (Azure Prompt Shields, Lakera) add weight if terms of service and budget allow.

**Hardware.** The 47GB Colab GPU fits every open guard above in bf16, including Llama Guard 4-12B at roughly 24GB of weights. The 20GB lab GPU fits the 8B models in bf16 but needs 8-bit loading for the 12B model [inference].

**Llama Guard 3.** It must be run for real, at 1B and 8B, with logged outputs and commit-stamped configs. The earlier documents' unrun comparison is an integrity liability. It is also a useful data point:

- It barely detects injections (28.28% malicious accuracy on PIGuard's set) ([arXiv 2410.22770v3](https://arxiv.org/html/2410.22770v3)).
- Its 1B variant has a 35.9% implied benign FPR, versus 2.7% for the 8B ([arXiv 2511.22047](https://arxiv.org/html/2511.22047v1)).
- It reached 0.48 obfuscation recall in PIDS-Bench ([arXiv 2609.15017](https://arxiv.org/html/2609.15017)).
- It lists Hindi among its 8 languages ([HF card](https://huggingface.co/meta-llama/Llama-Guard-3-8B) [not re-verified]).

A paired metric that penalizes both "paranoid" and "permissive" guards is exactly what Llama Guard 3 illustrates.

**Protocol requirements.**

- **Thresholds and calibration:** report each guard at its default threshold and at a matched clean-benign FPR. Report recall at 1% FPR, the metric LlamaFirewall uses ([arXiv 2505.03574](https://arxiv.org/pdf/2505.03574) [snippet]).
- **Benign sources:** use several held-out benign sources, not curated ones alone, given the PIDS-Bench and Liu findings.
- **Statistics:** use multiple seeds for any trained model and report confidence intervals.
- **Annotation:** report human agreement statistics for the benchmark.
- **Fairness metrics:** FPR parity gap, disparate-impact ratio, and FPR at matched English TPR.
- **Prior dataset:** download and inspect the Srinivasan et al. Kaggle data as an MT contrast.
- **Ecological validity:** reviewers will ask why a benign user would send Base64 or soft hyphens. The answer should be grounded in measured occurrence where possible: soft hyphens in copy-pasted PDF text, ZWJ in Devanagari, encoded payloads in developer workflows [inference]. Otherwise the paper should acknowledge that wrapper families are a stress test rather than natural traffic.

### Venues and timing

Paper 1's natural home is ACL Rolling Review, targeting ACL, EMNLP or NAACL main or Findings. That is where PIGuard ([ACL 2025](https://aclanthology.org/2025.acl-long.1468)), CSRT ([arXiv 2406.15481](https://arxiv.org/abs/2406.15481)) and MrGuard ([EMNLP 2025](https://aclanthology.org/2025.emnlp-main.1392.pdf)) appeared. COLM, which published PolyGuard, is an alternative ([arXiv 2504.04377](https://arxiv.org/abs/2504.04377v1)). Fallbacks include the LLMSEC workshop, which hosted Hackett et al. ([ACL Anthology](https://aclanthology.org/people/william-hackett/unverified/)), along with TrustNLP and the code-switching workshop CALCS. A fairness-centred version could go to FAccT or AIES. Submission deadlines were not verified in the notes and must be checked. The timing risk outweighs the venue choice: three directly relevant preprints appeared between 1 and 24 September 2026. The team should post to arXiv at submission and run a final sweep for "benign twin," "paired perturbation," "format bias" and "obfuscation over-defense" immediately before it.

## Paper 2's novelty lives in measurement and trade-offs, not in HMAC

### What is already done

**The attack is established prior art.**

- Microsoft's Context Compliance Attack injects a fabricated assistant turn ending in a yes/no question. It worked on all or nearly all tasks against Llama 3.1, Gemma 3 27B and Gemini 2 Flash, among others ([MSRC](https://www.microsoft.com/en-us/msrc/blog/2025/03/jailbreaking-is-mostly-simpler-than-you-think)).
- The Dialogue Injection Attack reports **0.82 ASR on GPT-4o** after 10 queries. It fully bypassed OpenAI Moderation and a perplexity filter, but it never tested Llama Guard or Prompt Guard as defenses ([arXiv 2503.08195](https://arxiv.org/html/2503.08195v1)).
- An IEEE S&P 2026 measurement found that **8 of 17 chatbot plugins**, used on about 8,000 websites, fail to protect history integrity. In those plugins, forgery raises unintended behavior 3–8× ([arXiv 2511.05797](https://arxiv.org/abs/2511.05797)).
- Many-shot jailbreaking ([NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/ea456e232efb72d261715e33ce25f208-Abstract.html)) and ChatBug ([arXiv 2406.12935](https://arxiv.org/pdf/2406.12935)) cover faux dialogue *inside* user text and template-token abuse.

**The defense is proposed and partially implemented nearby.** Microsoft's CCA post already proposes that providers "sign conversation histories with a secret key," without evaluating it ([MSRC](https://www.microsoft.com/en-us/msrc/blog/2025/03/jailbreaking-is-mostly-simpler-than-you-think)). Four 2026 papers come within one step:

| Work | Closest overlap with HMAC-signed history at a sidecar | Difference |
|---|---|---|
| Giovanny et al., "Verified History" ([arXiv 2609.35308](https://arxiv.org/html/2609.35308), 9 Oct 2026) | Orchestrator hashes history per turn, notes the hash must be keyed, restores on mismatch | Single model (Gemini-3.1 Flash-Lite). Compromised-middleware threat model. Useless against prompt-embedded attacks |
| Leong, "Recognition Without Enforcement" ([arXiv 2608.28502](https://arxiv.org/abs/2608.28502), 28 Aug 2026) | External reference monitor rejected all forged, tampered, replayed and unsigned requests. Adaptive red team found only a clock-skew bug | Signs instruction sources. HMAC-signed memory records are attributed to it only via [snippet, unverified] |
| Panfilov et al. ([arXiv 2608.09867](https://arxiv.org/html/2608.09867v1), Aug 2026) | Providers already MAC replayable reasoning blocks. The authors recommend binding the MAC to the preceding history | Reasoning blocks, not visible assistant text. Apparently a single global key |
| Luo et al., "Rewriting the Response Path" ([arXiv 2605.02187](https://arxiv.org/abs/2605.02187), May 2026) | Provider-signed fields verified by a local shim. Zero false rejections, 0.0167% overhead | Protects responses in transit, not replayed history |

Multi-turn attacks are mature. MHJ human jailbreaks exceed **70% ASR** against defenses reporting single-digit ASR ([arXiv 2408.15221](https://arxiv.org/abs/2408.15221v2)). X-Teaming reports up to 98.1% ASR ([arXiv 2504.13203](https://arxiv.org/pdf/2504.13203)). Crescendo ([arXiv 2404.01833](https://arxiv.org/pdf/2404.01833)) and ActorAttack ([arXiv 2410.10700](https://arxiv.org/abs/2410.10700v1)) are standard. Session-level guards are an active 2026 preprint area, mostly on self-built datasets:

- Defensive M2S ([arXiv 2601.00454](https://arxiv.org/pdf/2601.00454) [snippet])
- the proxy-level "Peak + Accumulation" ([arXiv 2602.11247](https://arxiv.org/pdf/2602.11247) [snippet])
- hierarchical-attention classifiers ([arXiv 2606.21082](https://arxiv.org/html/2606.21082v1) [snippet])
- Stateful Guardrails ([arXiv 2607.19361](https://arxiv.org/html/2607.19361))

Adaptive evaluation is now the bar. "The Attacker Moves Second" broke 12 defenses, most at over 90% ASR ([USENIX Sec '26](https://www.usenix.org/conference/usenixsecurity26/presentation/nasr)). Zhan et al. broke all 8 indirect-injection defenses they tested at over 50% ([NAACL Findings 2025](https://arxiv.org/html/2503.00061v2)).

### What remains open

**The open ground is the coupling of provenance with guard cost.** No paper found uses verified provenance to *skip* classifier scanning of genuine assistant turns, and so reduce session-level false positives and latency. False positives compound with turn count: for k independently scanned turns at per-turn FPR p, session FPR ≈ 1 − (1 − p)^k [inference]. The evidence for compounding is suggestive but thin. GuardSet-X reports Llama Guard 2 conversation FPR of 0.958 versus 0.774 per request in finance, but the table is hard to read and must be verified before citing ([arXiv 2506.19054](https://arxiv.org/html/2506.19054v2)). Stateful Guardrails finds benign-session FPR from 0.000 to 0.200 depending on threshold ([arXiv 2607.19361](https://arxiv.org/html/2607.19361)).

Three further gaps are open:

- **Guard-centric measurement.** No study measures how deployed guards and moderation APIs handle `assistant`-role content and forged turns: whether they scan those turns, and whether a forged turn flips their verdict.
- **Binding analysis.** No paper analyses a MAC over (session id, turn index, role, content hash, previous MAC) in a guard proxy. Panfilov et al. show that unbound MACs allow context transplantation, which makes this a concrete design point ([arXiv 2608.09867](https://arxiv.org/html/2608.09867v1)).
- **Laundering attack.** No paper evaluates the obvious adaptive counter: steer the model into producing a borderline turn, let the proxy sign it, then exploit the skip.

**Novelty is thin-to-moderate and must be framed honestly.** The primitive is trivial, and reviewers will say "HMAC over history at a trusted intermediary is known." The paper must also state what provenance cannot stop:

- Crescendo-style attacks, where every turn is genuine and therefore signed
- in-message faux dialogues
- chat-template tokens embedded in user text ([arXiv 2503.08195](https://arxiv.org/html/2503.08195v1); [arXiv 2406.12935](https://arxiv.org/pdf/2406.12935))

Reviewers will also ask "why not keep history server-side?" Microsoft notes that server-side-state products are not susceptible ([MSRC](https://www.microsoft.com/en-us/msrc/blog/2025/03/jailbreaking-is-mostly-simpler-than-you-think)). The paper needs a quantified answer: stateless, horizontally scaled sidecars and third-party plugins that forward client history, the very setting the S&P 2026 study found vulnerable ([arXiv 2511.05797](https://arxiv.org/abs/2511.05797)). It should also include server-side state as an explicit baseline for storage and latency [inference].

**Sharpened research question:** Can cryptographically bound provenance of assistant turns let a stateless guard proxy scan less, cutting session false positives and latency, without opening a new trust channel that a defense-aware multi-turn attacker can exploit?

**Contributions.**

1. A measurement of forged-history acceptance and handling across LLM APIs and guards: Llama Guard 3/4, Prompt Guard 2, ProtectAI, Qwen3Guard, NeMo, OpenAI Moderation, and Azure Prompt Shields where permitted. Whether providers authenticate assistant turns is itself unverified in the notes.
2. A bound per-turn MAC design with a formal threat model.
3. Empirical benign-session FPR and latency for scan-all vs skip-verified on benign multi-turn corpora, such as ShareGPT as used by Stateful Guardrails.
4. A defense-aware adaptive evaluation. Its components:
   - an X-Teaming-style red-team agent that knows about signing and skipping
   - laundering
   - replay, splice, truncation and cross-session reuse
   - MAC-format forgery
   - in-message faux dialogue
   - short-turn splitting against the previous-turn-context heuristic
   - GCG/TAP-style optimization against the ingress classifier
5. Evaluation on attack sets: CCA, DIA, MHJ, SafeDialBench ([arXiv 2502.11090](https://arxiv.org/pdf/2502.11090)), MultiBreak ([ICML 2026](https://icml.cc/virtual/2026/poster/63523)) and X-Teaming. Comparison against Peak+Accumulation, Defensive M2S, Llama Guard with conversation context, and a server-side-state baseline.

MT-JailBench shows multi-turn ASR depends heavily on judge and flow-control choices, so the judge, retry and refusal policies must be reported ([arXiv 2605.11002](https://arxiv.org/html/2605.11002v1)).

### Venues

USENIX Security '27 requires an Open Science appendix and has a 13-page body. Its cycle-2 deadline is **26 January 2027**, with registration on 19 January ([CFP](https://www.usenix.org/node/321195); [CFP PDF](https://www.usenix.org/sites/default/files/sec27_cfp-070826.pdf)). That falls at the very start of semester 8, which is too early for work that has not begun. **SaTML is the most realistic first target** for a careful, smaller-scale student study. CCS, S&P and NDSS are stretch targets, and ACSAC, AISec and DLSP are fallbacks. None of these deadlines were verified in the notes. If commercial guards or APIs are bypassed, vendor disclosure and an ethics appendix are expected [inference].

### The entropy circuit breaker is a component, not a paper

The optional entropy-triggered hallucination check should be cut from Paper 2. The evidence is consistent:

- **Raw token entropy is a weak hallucination trigger on long-form text.** It reaches about 0.742 AUC on LongFact and 0.665 on HealthBench for Llama-3.1-8B, against 0.85–0.90 for hidden-state probes ([arXiv 2509.03531](https://arxiv.org/html/2509.03531v2)). Every hallucination the gate misses never reaches the verifier.
- **The verifier is weak.** The team's zero-shot `nli-deberta-v3-small` scores 60% / AUROC 0.61 on HaluEval-QA. Purpose-built verifiers do far better: MiniCheck-FT5 reaches 74.7% balanced accuracy on LLM-AggreFact ([arXiv 2404.10774](https://arxiv.org/html/2404.10774v2)), LettuceDetect 79.22% F1 on RAGTruth ([arXiv 2502.17125](https://arxiv.org/html/2502.17125v1)), and HHEM-2.1-Open 74.28% on RAGTruth-QA ([HF card](https://huggingface.co/vectara/hallucination_evaluation_model) [snippet]).
- **The components are already published.**
  - DRAD's entropy-triggered real-time detection plus retrieval ([arXiv 2407.09417](https://arxiv.org/abs/2407.09417v1))
  - FLARE's low-confidence-triggered retrieval ([arXiv 2305.06983](https://ar5iv.labs.arxiv.org/html/2305.06983))
  - Qwen3Guard-Stream's consecutive-token debounce ([HF card](https://huggingface.co/Qwen/Qwen3Guard-Stream-0.6B))
  - streaming halts in SCM ([arXiv 2506.09996](https://arxiv.org/pdf/2506.09996)) and Kelp/PlugGuard ([arXiv 2510.09694](https://arxiv.org/pdf/2510.09694))
- **SelfCheckGPT is a strawman latency foil.** It is zero-resource and uses 20 samples per passage ([arXiv 2303.08896](https://ar5iv.labs.arxiv.org/html/2303.08896)).
- **It is trivially evaded at a security venue.** Any attack that makes the model *confident* bypasses an entropy gate [inference].

If the team later revives it, the defensible framing is a training-free, logprob-only streaming grounding guard aimed at an NLP venue. That version would need:

- a MiniCheck- or HHEM-class verifier
- gate-on vs gate-off Pareto curves of verifier calls saved against recall lost
- trigger recall reported separately
- time-to-detection and false-stop rate
- RAGTruth plus a long-form set
- comparisons against DRAD, FLARE and a linear probe

## Prioritized next steps

Paper 1 should come first. Its gap is clearer, its data asset is unique to this team, and its competition is moving weekly. Paper 2 should be reframed now so semester-7 slack can go into its cheapest experiment: measuring how guards handle forged turns.

| Priority | Action | Why now |
|---|---|---|
| 1 | Strike or correct the unrun Llama-Guard-3 claim in every project document. Then run Llama Guard 3-1B and 8B with logged, commit-stamped outputs | An unrun comparison discovered by a reviewer would sink both papers. The real run is also a useful data point |
| 2 | Do a novelty sweep within two weeks. Read 2609.26176, 2609.15017 and 2609.01046 in full, including HiveTraceGuard-Pro Table 13. Check 2608.01373, 2608.08641, Fairoze et al., PolyGuard/Qwen3Guard per-language FPR, the Horizon-Labs card, and CALCS/WOAH 2025–26. Download the Srinivasan Kaggle data and the PIDS-Bench code | The three closest preprints are under a month old. A missed one is the largest single risk |
| 3 | Freeze the Paper 1 spec: perturbation families, scaffold arm, paired metric, within-perturbation AUROC, fairness metrics, thresholds | Prevents scope drift and makes the cross-guard harness reusable |
| 4 | Build the cross-guard harness and run the obfuscation half first, on about 15 guards using the 47GB GPU | It is cheap, fast, and gives early evidence of rank reversals |
| 5 | Write annotation guidelines and author the native Hindi/Devanagari/romanized/Hinglish benign and injection set, with a trigger-word split, spelling variants, agreement statistics and an MT contrast | This is the most novel and most time-consuming contribution |
| 6 | Run the token-fertility analysis and the mitigation ablation: script-aware normalization vs augmentation vs both, held-out families, decode-and-rescan | Turns the audit into a top-tier paper. Script-aware normalization avoids breaking Devanagari ZWJ |
| 7 | Write Paper 1, verify ARR dates, and post to arXiv at submission | Establishes priority in a fast-moving niche |
| 8 | Paper 2: write the threat model, then measure how APIs and guards handle forged assistant turns and benign-session FPR (scan-all vs skip-verified) | The cheapest, most novel part of Paper 2, and it can start in semester 7 |
| 9 | Paper 2: build the defense-aware red-team agent and the laundering, replay and splice attacks, plus a server-side-state baseline; target SaTML | Adaptive evaluation is now the minimum bar for security venues |

## Conclusion

The field's evaluation habit is lopsided. Evasion studies score only attacks, and multilingual studies score only under-blocking. As a result, a guard that refuses everything unfamiliar can look *more* robust than one that actually reads intent. GuardShield's most valuable insight is that its own failure, flagging most obfuscated and Hindi benign text, is a measurable property of a whole class of detectors. That makes it a contribution rather than an embarrassment, provided it is measured in pairs. The paired design also makes the two halves of Paper 1 one claim about format-versus-intent sensitivity, not two loosely joined studies. The within-perturbation AUROC split is the sharpest tool for telling reviewers whether the fix is recalibration or retraining.

For Paper 2, the lesson runs the other way: the engineering the team already built is not where the novelty lies. HMAC-signed history is a sound design choice, but its research value appears only when the team measures what it buys (fewer compounded false positives, lower latency) and what it costs: a new trusted channel that an attacker can launder content through. A paper that honestly reports where provenance fails is more publishable than one claiming it solves multi-turn attacks.
