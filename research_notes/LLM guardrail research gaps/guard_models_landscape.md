# Landscape of Prompt-Injection / Jailbreak Guardrail Models and LLM Guard Systems (focus: over-defense, multilingual, obfuscation, multi-turn)

Research date: 2026-10-12. Provenance key used below:
- **[V]** means verified by fetching the cited page during this session.
- **[S]** means it comes only from a search-result snippet or secondary summary, so check it before quoting in a paper.
- **[K]** means it comes from prior knowledge of a well-known primary source. The URL is the canonical one but was **not re-fetched** this session. Re-verify the exact numbers before citing.

---

## Key Question 1: Catalog of guard systems (size, scope, languages, reported FP/over-defense, multi-turn, weaknesses)

### Takeaway
Small encoder classifiers dominate dedicated prompt-injection detection: Prompt Guard 1/2, ProtectAI, deepset, PIGuard/InjecGuard, GenTel-Shield and Sentinel. Their over-defense varies enormously and depends on the dataset. PIGuard is the only one designed explicitly around over-defense (NotInject). Prompt Guard 2 is the only one with an explicit low-FPR training objective plus multilingual evaluation that includes Hindi. LLM-based safety guards (Llama Guard 1-4, WildGuard, ShieldGemma, Granite Guardian, Aegis/NemoGuard, Qwen3Guard, PolyGuard) target harmful content more than injection. Some of them, such as Llama Guard and Qwen3Guard, take conversation context. None of the systems surveyed reports false-positive rates on benign *obfuscated* text or on *romanized code-mixed* text such as Hinglish.

### Cited Findings

#### A. Dedicated prompt-injection / jailbreak classifiers

**Meta Prompt Guard v1 (86M)**
- Built on mDeBERTa-v3-base (86M backbone) with 3 labels (BENIGN / INJECTION / JAILBREAK), a 512-token window, and multilingual input. Released July 2024. [K] — [HF card](https://huggingface.co/meta-llama/Prompt-Guard-86M)
- On the Prompt Guard 2 card's own benchmark, v1 reaches AUC .987 (English) and .983 (multilingual) but only **21.2% recall at 1% FPR**. Its APR on AgentDojo at 3% utility reduction is 67.6%. [V] — [Llama Prompt Guard 2 card](https://huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M)
- Severe over-defense: on NotInject, PromptGuard (v1) scores **0.88%** over-defense accuracy, meaning it flags almost all 339 benign trigger-word sentences. It scores 26.82% benign accuracy and 97.10% malicious accuracy. Per difficulty level it gets 2.65% / 0.00% / 0.00% on 1/2/3 trigger words. [V] — [InjecGuard/PIGuard arXiv 2410.22770v3, Tables 1 & 7](https://arxiv.org/html/2410.22770v3)
- In GenTel-Bench, Prompt Guard's precision is about 50-51% with 97-100% recall: accuracy 50.58% on jailbreak, 50.90% on goal hijacking and 50.28% on prompt leaking. In other words, it labels nearly everything as an attack. On non-English translations its accuracy ranged from 44.53% (German) to 71.04% (Japanese). [V] — [GenTel-Safe arXiv 2409.19521](https://arxiv.org/html/2409.19521v1)
- PINT score 61.8% (2025-05-02). The score covers jailbreak detection only. [V] — [Lakera PINT repo](https://github.com/lakeraai/pint-benchmark)
- Evasion results: average character-injection ASR of 70.44% on prompt injection and 73.08% on jailbreak, and AML-evasion ASR of 2.76% (PI) and 12.66% (JB). [V] — [Hackett et al., arXiv 2504.11168 (LLMSec 2025)](https://arxiv.org/html/2504.11168v3)
- On AgentDojo-Clean tool outputs, v1 has an FPR of 31.9% at its default threshold. [V] — [Liu, arXiv 2610.03448](https://arxiv.org/html/2610.03448)

**Llama Prompt Guard 2 (22M and 86M), released April/May 2025**
- The 86M model uses an mDeBERTa-base backbone. The 22M model uses DeBERTa-xsmall and is English-centric, with no multilingual pretraining. Both use a 512-token window; the card recommends splitting longer inputs and scanning the segments in parallel. Labels are binary benign/malicious, and the separate INJECTION label was removed. The card defines "malicious" as an input that "explicitly attempts to override prior instructions" regardless of harm. [V] — [HF card](https://huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M)
- Reported results on the card:

| Model | AUC (English) | Recall @ 1% FPR (English) | AUC (multilingual) | Latency |
|---|---|---|---|---|
| 86M | .998 | 97.5% | .995 | 92.4 ms on A100 at 512 tokens |
| 22M | .995 | 88.7% | .942 | 19.3 ms |

  On AgentDojo, APR at 3% utility loss is 81.2% (86M) and 78.4% (22M). Baselines on the same measure: ProtectAI 22.2%, deepset 13.5%, LLM Warden 12.9%. [V] — [HF card](https://huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M)
- Multilingual evaluation covers English, French, German, **Hindi**, Italian, Portuguese, Spanish and Thai. The card does not say whether romanized Hindi (Hinglish) was included. [V] — [HF card](https://huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M)
- Over-defense design: an energy-based loss "improves precision on out-of-distribution data" and "reduces false positives". Tokenization was modified to resist "whitespace manipulations and fragmented tokens". The card has no explicit over-defense benchmark. Limitations include adaptive attacks, application-specific attacks, and a weaker 22M model on multilingual input. [V] — [HF card](https://huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M)
- Prompt Guard 2 is part of LlamaFirewall alongside AlignmentCheck and CodeShield. LlamaFirewall uses recall at 1% FPR as its primary operating metric. [S] — [LlamaFirewall arXiv 2505.03574](https://arxiv.org/pdf/2505.03574)
- PINT score is 78.76% for the 86M model (2025-05-05). [V] — [PINT repo](https://github.com/lakeraai/pint-benchmark)
- Independent tool-output FPR is near zero: 0.0% (22M) and 0.6% (86M) on AgentDojo-Clean, and 0.0% on τ-bench. [V] — [arXiv 2610.03448](https://arxiv.org/html/2610.03448)
- Weak on obfuscated attacks in PIDS-Bench: obfuscation recall is only **0.3235** (leetspeak, homoglyph and zero-width attacks). [V] — [PIDS-Bench arXiv 2609.15017](https://arxiv.org/html/2609.15017)
- WAInjectBench reports that "PromptGuard generalizes poorly" on web-agent injections. [S] — [arXiv 2510.01354](https://arxiv.org/pdf/2510.01354)

**ProtectAI deberta-v3-base-prompt-injection (v1, 2023) and -v2 (2024)**
- v2 is a fine-tune of microsoft/deberta-v3-base, about 0.2B parameters, licensed Apache-2.0. Its training mixes multiple public datasets: the header says "7 datasets", while the license table lists 22 sources. [V] — [HF card v2](https://huggingface.co/protectai/deberta-v3-base-prompt-injection-v2)
- The project is now **archived**. [V] — [HF card v2](https://huggingface.co/protectai/deberta-v3-base-prompt-injection-v2)
- The card states the model is **English only** and **does not detect jailbreaks**. On 20k prompts from datasets it was not trained on, it reports accuracy 95.25%, precision 91.59% and recall 99.74%. The card also warns: "we do not recommend using this scanner for system prompts, as it produces false-positives". [V] — [HF card v2](https://huggingface.co/protectai/deberta-v3-base-prompt-injection-v2)
- NotInject over-defense accuracy is 56.64% (by trigger count: 76.11% / 47.79% / 46.02%), with benign accuracy 86.20% and malicious accuracy 48.60%. [V] — [arXiv 2410.22770v3](https://arxiv.org/html/2410.22770v3)
- PINT score 79.14%. [V] — [PINT](https://github.com/lakeraai/pint-benchmark)
- Hackett et al. measured character-injection ASR of 20.26% for v2 and 77.32%/51.39% for v1 (PI/JB). AML-evasion ASR was 67.87% for v2 and 95.18% for v1 (PI). [V] — [arXiv 2504.11168v3](https://arxiv.org/html/2504.11168v3)
- Tool-output FPR for v2 is **30.1%** on AgentDojo and **66.9%** on τ-bench. On general text it is much lower: 0.5% on web pages and 1.2% on emails. Blocking on v2 would stop 69.1% of AgentDojo tasks. [V] — [arXiv 2610.03448](https://arxiv.org/html/2610.03448)
- In PIDS-Bench, the hard-benign FPR is 0.216 at τ=0.5 [S], the structural-shift FPR (JSON wrapping and similar) is 0.4525, and obfuscation recall is 0.906. [V] — [PIDS-Bench](https://arxiv.org/html/2609.15017)
- The CAPTURE paper reports that InjecGuard and ProtectAIv2 have high FPR and FNR on context-aware data. [S] — [CAPTURE arXiv 2505.12368](https://arxiv.org/pdf/2505.12368)

**deepset/deberta-v3-base-injection (2023)**
- A DeBERTa-v3-base fine-tune on the small deepset/prompt-injections dataset (English plus some German). [K] — [HF card](https://huggingface.co/deepset/deberta-v3-base-injection)
- NotInject over-defense accuracy is **5.31%** and benign accuracy is 34.06%. [V] — [arXiv 2410.22770v3](https://arxiv.org/html/2410.22770v3)
- In GenTel-Bench it reaches 100% recall but only 57-61% precision. [V] — [arXiv 2409.19521](https://arxiv.org/html/2409.19521v1)
- APR on AgentDojo is 13.5%, as reported by Meta. [V] — [Prompt Guard 2 card](https://huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M)
- In PIDS-Bench, a "DeBERTa-PI" detector has hard-benign FPR 0.804 at τ=0.5 [S] and structural-shift FPR 1.000 [V]. Which HF checkpoint "DeBERTa-PI" refers to was not confirmed. — [PIDS-Bench](https://arxiv.org/html/2609.15017)

**fmops/distilbert-prompt-injection**
- NotInject over-defense accuracy is 5.60%. [V] — [arXiv 2410.22770v3](https://arxiv.org/html/2410.22770v3)
- CAPTURE reports "100% FNR in Fmops and 100% FPR in PromptGuard" on its context-aware datasets. [S] — [arXiv 2505.12368](https://arxiv.org/pdf/2505.12368)

**InjecGuard → PIGuard (Li, Liu, Zhang, Xiao; arXiv Oct 2024; ACL 2025 main as "PIGuard")**
- Venue and model: ACL 2025 long paper ([ACL Anthology](https://aclanthology.org/2025.acl-long.1468)), weights at [HF leolee99/PIGuard](https://huggingface.co/leolee99/PIGuard). [S] The backbone is DeBERTa-v3-base class, with about 60.45 GFLOPs and 15.34 ms per inference. [V] — [arXiv 2410.22770v3](https://arxiv.org/html/2410.22770v3)
- NotInject construction:
  - 113 trigger words were mined by comparing word frequencies in benign and malicious data, then filtered by GPT-4o-mini and three human raters.
  - The dataset has 339 benign sentences, 113 each at the 1-, 2- and 3-trigger-word levels.
  - Categories are Common Queries, Techniques, Virtual Creation and Multilingual.
  - [V] — [arXiv 2410.22770v3](https://arxiv.org/html/2410.22770v3)
- MOF ("Mitigating Over-defense for Free") works in four steps. First, train normally. Second, feed every vocabulary token alone into the model and treat tokens flagged as attacks as biased. Third, have GPT-4o-mini generate 1,000 benign samples from combinations of those tokens. Fourth, retrain from scratch with the new samples. [V] — [arXiv 2410.22770v3](https://arxiv.org/html/2410.22770v3)
- Results (Table 1, accuracy %; "Over-defense" is accuracy on NotInject):

| Model | Over-defense | Benign | Malicious | Average |
|---|---|---|---|---|
| InjecGuard | 87.32 | 85.74 | 77.39 | 83.48 |
| LakeraGuard | 87.61 | 90.89 | 53.19 | 77.23 |
| GPT-4o | 86.73 | 90.78 | 79.10 | 85.53 |
| LlamaGuard3 | 99.71 | 95.18 | 28.28 | 74.39 |
| ProtectAIv2 | 56.64 | 86.20 | 48.60 | 63.81 |

  Llama Guard 3 is near-perfect on benign text only because it barely detects injections. [V] — [arXiv 2410.22770v3](https://arxiv.org/html/2410.22770v3)
- Independent re-evaluation puts the AgentDojo-Clean FPR at **29.5%** and the τ-bench FPR at 11.0%. PIGuard ranks first on BIPIA (TPR 95.1%) but gets only 2.1% on AgentDojo. The training split contains 1,116 BIPIA inputs, including 65 of the 75 train-half text attacks, and 53 of the 62 InjecAgent attacks. In other words, it is **benchmark-contaminated** with respect to BIPIA and InjecAgent train data. [V] — [arXiv 2610.03448](https://arxiv.org/html/2610.03448)

**GenTel-Shield / GenTel-Bench (GenTel.io + Zhejiang Univ., arXiv Sept 2024)**
- The detector is fine-tuned from a **multilingual E5** embedding model; the paper does not state the parameter count. Training data comes from jailbreakchat, reddit, VMware Open-Instruct and Chatbot Instruction Prompts, with synonym/insertion/swap/deletion and LLM-rewrite augmentation. [V] — [arXiv 2409.19521](https://arxiv.org/html/2409.19521v1)
- GenTel-Bench has 84,812 attacks across 3 categories (jailbreak, goal hijacking, prompt leaking) and 28 scenarios. It is balanced 1:1 with benign data from 10 application scenarios, for more than 170k items in total. [V] — [arXiv 2409.19521](https://arxiv.org/html/2409.19521v1)
- Multilingual evaluation uses machine-translated zh/ja/fr/es/de versions of the data. [V] — [arXiv 2409.19521](https://arxiv.org/html/2409.19521v1)
- Reported accuracy is 97.63% on jailbreak and 96.81% on goal hijacking. Precision is 98-99.6%, which is the paper's only FP proxy; no explicit FPR is given. [V] — [arXiv 2409.19521](https://arxiv.org/html/2409.19521v1)
- The prompt-leaking table lists GenTel-Shield accuracy as "7.92". This is internally inconsistent with the reported precision and recall and is probably a typo. [V] — [arXiv 2409.19521](https://arxiv.org/html/2409.19521v1)

**Other 2025-2026 encoder detectors that appear in independent evaluations**
- The following were all evaluated in one study: Qualifire Sentinel and Sentinel v2, Sheltron, Prismor-1.5B, Wolf Defender, Horizon-Labs, TestSavant-L, JasperLS, and ProtectAI v2-small.
  - Horizon-Labs had 0.0% AD-Clean FPR and the best agent-benchmark TPR.
  - JasperLS had 78.5% and 93.1% FPR on the two agent benchmarks.
  - [V] — [arXiv 2610.03448](https://arxiv.org/html/2610.03448)
- CourtGuard reports Sentinel at 97.6% versus ProtectAI deberta-v3-base at 65.2% on the Qualifire benchmark. [S] — [arXiv 2510.19844](https://arxiv.org/pdf/2510.19844)
- PromptShield (Jacob, ..., Wagner; ACM CODASPY 2025) is a benchmark plus detector built specifically for the **low-FPR regime**. Its benign data covers both conversational and application-structured inputs. [V for the abstract; per-detector numbers not retrieved] — [arXiv 2501.15145](https://arxiv.org/abs/2501.15145)

#### B. Commercial / API guards

**Lakera Guard (commercial API) and PINT benchmark**
- PINT has 4,314 inputs: 3,016 English and 1,298 non-English. The non-English data covers Indo-European, Asian (zh/ja/ko/vi/th) and other languages (fi/hu/ar/tr). Hindi is not listed among the examples. [V] — [PINT repo](https://github.com/lakeraai/pint-benchmark)
- Composition: prompt injections 5.2%, jailbreaks 0.9%, **hard negatives 20.9%**, chats 36.5%, public documents 36.5%. That makes PINT about 94% benign, so it heavily weights false positives. [V] — [PINT repo](https://github.com/lakeraai/pint-benchmark)
- The dataset is part-proprietary and not public; the repo is now archived.
- Leaderboard: Lakera Guard 95.22%, AWS Bedrock Guardrails 89.24%, Azure Prompt Shield 89.12%, ProtectAI v2 79.14%, Prompt Guard 2 86M 78.76%, Google Model Armor 70.07%, Aporia 66.44%, Prompt Guard v1 61.82%. [V] — [PINT repo](https://github.com/lakeraai/pint-benchmark)
- Caveat: the benchmark is vendor-run. Lakera says its own model was not trained on PINT inputs, but there is no third-party audit. [V statement / inference on independence]
- On NotInject, Lakera Guard scores 87.61% over-defense accuracy but has 710 ms latency and only 53.19% malicious accuracy. [V] — [arXiv 2410.22770v3](https://arxiv.org/html/2410.22770v3)

**Azure AI Content Safety Prompt Shields (Microsoft)**
- Two shields:
  - "User prompt attacks" (formerly Jailbreak risk detection), with subtypes: change system rules, embedded conversation mockup, role-play, and **encoding attacks** (character transformations and ciphers).
  - "Document attacks" (indirect injection).
- The API takes a `userPrompt` plus up to 5 `documents`.
- Spotlighting (base64-tagging of untrusted documents) is in preview.
- The docs' troubleshooting for **false positives** is to switch from block to annotate mode, review subtypes, and exempt trusted sources. No FP rates are published on this page, and the doc page fetched (updated 2026-09) does not list supported languages.
- [V] — [Microsoft Learn](https://learn.microsoft.com/en-us/azure/ai-services/content-safety/concepts/jailbreak-detection)
- Independent results:
  - PINT score 89.12% for Documents + User Prompts. [V] — [PINT](https://github.com/lakeraai/pint-benchmark)
  - Character-injection ASR of 71.98% (PI) and 60.15% (JB). [V] — [arXiv 2504.11168v3](https://arxiv.org/html/2504.11168v3)
  - Word-importance rankings from ProtectAI v2 transfer and raise ASR against Azure, for example TextFooler PI from 63.03% to 72.06%. [V] — [arXiv 2504.11168v3](https://arxiv.org/html/2504.11168v3)

**Other commercial guards**
- AWS Bedrock Guardrails, Google Model Armor and Aporia appear only on the PINT leaderboard, with scores listed above. [V] — [PINT](https://github.com/lakeraai/pint-benchmark)
- Vijil Prompt Injection had the worst character-injection ASR among the six systems tested: 87.95% (PI) and 91.67% (JB). [V] — [arXiv 2504.11168v3](https://arxiv.org/html/2504.11168v3)

#### C. Frameworks / toolkits

**NVIDIA NeMo Guardrails**
- A programmable rails framework built on Colang.
- Its jailbreak "heuristics" rail uses two GPT-2-large **perplexity** heuristics: length/perplexity and prefix/suffix perplexity. Default thresholds are 89.79 and 1845.65, and they are fit on malicious and benign prompts. It is positioned as low-cost compared with the LLM `self check input` rail.
- If the detector endpoint is unavailable, the rail fails open: it logs, allows the request and returns no error.
- [S, official NVIDIA docs per snippet] — [NeMo Guardrails jailbreak protection docs](https://docs.nvidia.com/nemo/guardrails/latest/configure-guardrails/guardrail-catalog/jailbreak-protection)
- Inference: perplexity heuristics will by design flag benign high-perplexity text, such as obfuscated, code-mixed or non-English text. That makes them a natural over-defense case study, though this is not measured in the docs.
- A model-based "jailbreak detection model" flow exists (NemoGuard JailbreakDetect, embedding plus classifier). Its details were seen only on a third-party mirror. [S] — [mintlify mirror](https://mintlify.com/NVIDIA-NeMo/Guardrails/built-in/jailbreak-detection)
- NeMo Guard Jailbreak Detect had 72.54% character-injection ASR and 65.22% AML ASR on jailbreaks, the highest AML ASR of the six systems. [V] — [arXiv 2504.11168v3](https://arxiv.org/html/2504.11168v3)
- **Multi-turn:** an open GitHub feature request says the existing jailbreak rail judges one message at a time. It proposes a sliding window of 8 turns for Crescendo-style attacks. This is a proposal, not a shipped feature. [S] — [NeMo Guardrails issue #2028](https://github.com/NVIDIA-NeMo/Guardrails/issues/2028)

**Rebuff (Protect AI)**
- Multi-layer prompt-injection detector: heuristics, an LLM-based check, a vector DB of previous attacks, and canary tokens for leak detection.
- The GitHub repo is archived and marked as a prototype.
- No benchmark or FP numbers are published.
- [K] — [GitHub protectai/rebuff](https://github.com/protectai/rebuff)

**LLM Guard (Protect AI)**
- Open-source library of input and output scanners: PromptInjection, Toxicity, BanTopics, Secrets, Anonymize and others.
- The PromptInjection scanner wraps the ProtectAI deberta-v3 prompt-injection model, so it inherits that model's English-only limits and FP behavior.
- [K] — [GitHub protectai/llm-guard](https://github.com/protectai/llm-guard)

#### D. LLM-based safety guards (harm moderation; some include a jailbreak category)

**Llama Guard 1 (7B, Dec 2023)**
- Llama-2-7B base with an instruction-following taxonomy of 6 categories.
- Classifies prompts and responses with the **conversation provided as context**.
- [K] — [arXiv 2312.06674](https://arxiv.org/abs/2312.06674)

**Llama Guard 2 (8B, Llama 3, Apr 2024)**
- Uses an MLCommons-aligned 11-category taxonomy.
- English-focused.
- [K] — [HF card](https://huggingface.co/meta-llama/Meta-Llama-Guard-2-8B)

**Llama Guard 3 (8B and 1B; 11B-Vision; Jul–Sep 2024)**
- Covers 14 categories (S1-S14) and 8 languages: en, fr, de, hi, it, pt, es, th.
- [K] — [HF card](https://huggingface.co/meta-llama/Llama-Guard-3-8B)
- Hardly detects injections. On NotInject, Llama Guard 3 gets 99.71% over-defense accuracy but only **28.28% malicious accuracy**. [V] — [arXiv 2410.22770v3](https://arxiv.org/html/2410.22770v3)
- Llama Guard 3-1B has a 35.9% implied FPR on benign OpenAssistant and JailbreakBench-benign prompts, versus 2.7% for the 8B model. [V] — [Young, arXiv 2511.22047](https://arxiv.org/html/2511.22047v1)

**Llama Guard 4 (12B, Apr 2025)**
- A dense model pruned from Llama 4 Scout. It is natively multimodal (text plus multiple images) and covers S1-S14, with S14 being code-interpreter abuse.
- Multilingual evaluation covers fr, de, **hi**, it, pt, es, th.
- On Meta's in-house output-filtering set:
  - English: recall 69%, **FPR 11%**, F1 61%, which is −3 points of FPR versus LG3.
  - Multilingual: recall 43%, FPR 3%, F1 51%.
- The card says the model "may be susceptible to adversarial attacks or prompt injection attacks" and redirects users to Prompt Guard 2 for prompt-attack detection.
- The card does not state multi-turn evaluation; it points to the blog for multi-turn inference.
- [V] — [HF card](https://huggingface.co/meta-llama/Llama-Guard-4-12B)

**WildGuard (AI2, 7B on Mistral-7B, Jun 2024)**
- Three tasks: prompt harmfulness, response harmfulness and refusal detection.
- Training data is WildGuardMix (about 92K items, including adversarial benign prompts); the test set is WildGuardTest (about 5.3K).
- English only.
- [K] — [arXiv 2406.18495](https://arxiv.org/abs/2406.18495); refusal-classifier use for XSTest per the [HF card](https://huggingface.co/allenai/wildguard) [S]
- Independent results:
  - Benign accuracy 91.8% (implied FPR 8.2%). [V] — [arXiv 2511.22047](https://arxiv.org/html/2511.22047v1)
  - PHTest benign accuracy of only 77.03%, versus 94.80% for Llama Guard 3 and 93.21% for LG4. The PHTest set consists of harmless prompts with superficially unsafe cues. [S] — [arXiv 2609.33634](https://arxiv.org/html/2609.33634)

**ShieldGemma (Google; 2B/9B/27B on Gemma 2; Jul 2024)**
- Covers 4 harm types: sexual, dangerous, harassment and hate.
- English.
- [K] — [arXiv 2407.21772](https://arxiv.org/abs/2407.21772)
- Independent benign FPR is low (2B 5.7%, 9B 4.1%) but recall is also low (overall accuracy 62.4% and 54.7%). The 2B model is very prompt-template sensitive, with a 20.7-point accuracy range. [V] — [arXiv 2511.22047](https://arxiv.org/html/2511.22047v1)

**IBM Granite Guardian (3.0 2B/8B Dec 2024; 3.1; 3.2 5B; 3.3 8B)**
- Risk dimensions include harm, social bias, profanity, violence, sexual content, unethical behavior and **jailbreak**.
- Also covers RAG hallucination (context relevance, groundedness, answer relevance) and function-call hallucination.
- [K] — [arXiv 2412.07724](https://arxiv.org/abs/2412.07724)
- Independent benign FPR: 3.3-8B about 12.0%, 3.2-5B about 34%. The paper itself is inconsistent here: Section 4.7 says 25.7%, while Table 3 implies about 34%. [V] — [arXiv 2511.22047](https://arxiv.org/html/2511.22047v1)
- Over-defense grows as trigger cues accumulate (cue-stacking), for Granite, WildGuard and Qwen3Guard alike. [S] — [arXiv 2609.33634](https://arxiv.org/html/2609.33634)

**NVIDIA Aegis / NemoGuard / Nemotron Safety**
- Aegis 1.0 (Apr 2024) is a 13-category taxonomy plus PEFT-tuned LlamaGuard experts. [K] — [arXiv 2404.05993](https://arxiv.org/abs/2404.05993)
- Aegis 2.0 (Jan 2025) is a dataset with commercial-use licensing and the basis for Llama-3.1-NemoGuard-8B-ContentSafety. [K] — [arXiv 2501.09004](https://arxiv.org/abs/2501.09004)
- NemoGuard-8B has an English prompt F1 of 82.9 in the Qwen3Guard comparison. [V] — [Qwen3Guard arXiv 2510.14276](https://arxiv.org/html/2510.14276v1)
- Nemotron-Safety-8B: benign FPR about 10.2%, and in 13.6% of responses it fell into "helpful mode", generating harmful content instead of classifying it. [V] — [arXiv 2511.22047](https://arxiv.org/html/2511.22047v1)
- A secondary summary of an Artificial Analysis / NVIDIA ranking describes the Nemotron models as "most restrictive (high recall, more false positives)" and Llama Guard and ShieldGemma as the most permissive. [S, secondary news] — [AlphaSignal summary](https://alphasignal.ai/news/artificial-analysis-ranks-20-ai-safety-guards-and-wildguard-wins)

**Qwen3Guard (Alibaba Qwen, Oct 2025)**
- Two variants, Gen and Stream, each at 0.6B, 4B and 8B, supporting **119 languages and dialects**. Labels are safe / controversial / unsafe, with strict and loose modes. **Jailbreak** is a category for prompts only.
- Stream adds token-level heads for real-time moderation during generation. It averages about 2 points below Gen. It hits the human-annotated unsafe sentence about 86.0% of the time, and in thinking mode it detects unsafe content within the first 128 tokens about 66.8% of the time.
- English prompt F1 averages 88.1 (0.6B), 89.3 (4B) and 90.0 (8B), versus PolyGuard-Qwen-7B 87.0, WildGuard-7B 85.8 and NemoGuard-8B 82.9.
- On RTP-LX prompts the 8B model averages 85.0, versus 80.9 for PolyGuard.
- The authors' Limitations section says it may flag content from some cultural groups as unsafe, and that Stream may have higher FP/FN rates in low-resource or out-of-distribution settings.
- [V] — [arXiv 2510.14276](https://arxiv.org/html/2510.14276v1)
- Independently, Qwen3Guard-8B has the top overall accuracy (85.3%) with an implied benign FPR of 8.8%. However, accuracy collapsed from **91.0 to 33.8** on novel versus public prompts, which suggests training-data overlap. [V] — [arXiv 2511.22047](https://arxiv.org/html/2511.22047v1)

**PolyGuard (COLM 2025)**
- A multilingual safety classifier covering 17 languages, including Hindi.
- Training data is PolyGuardMix (1.91M samples), drawn from real multilingual conversations plus machine-translated WildGuardMix. The evaluation set is PolyGuardPrompts (about 29K, machine-translated).
- The authors claim +5.5% over open and commercial classifiers.
- [S] — [arXiv 2504.04377](https://arxiv.org/pdf/2504.04377); [PolyGuardMix card](https://huggingface.co/datasets/ToxicityPrompts/PolyGuardMix/blob/main/README.md)

**Other multilingual guards (found, not deeply inspected)**
- MrGuard (EMNLP 2025) is a reasoning guardrail that reports robustness to **code-switching** between English and one other language. It does not separate false positives on benign code-mixed text. [S] — [arXiv 2504.15241](https://arxiv.org/html/2504.15241v3); [ACL Anthology](https://aclanthology.org/2025.emnlp-main.1392.pdf)
- X-Guard (multilingual guard, about 132 languages, 2025). [K] — [arXiv 2504.08848](https://arxiv.org/abs/2504.08848)
- HaloGuard 1.0 (2026) is an open-weights constitutional classifier for multilingual safety. [S] — [arXiv 2607.02079](https://arxiv.org/html/2607.02079v1)
- ML-Bench&Guard (2026) is a policy-grounded multilingual benchmark that reports over-refusal as FPR. [S] — [arXiv 2605.00689](https://arxiv.org/html/2605.00689v1)

#### E. Multi-turn / session guarding (state of the art)
- Several 2026 preprints treat multi-turn jailbreak detection as conversation-level classification:
  - Hierarchical attention transformers, capped at 24 turns and trained on a self-built 14,038-sample set. [S] — [arXiv 2606.21082](https://arxiv.org/html/2606.21082v1)
  - Defensive M2S, which compresses multi-turn conversations into single-turn guard input. [S] — [arXiv 2601.00454](https://arxiv.org/pdf/2601.00454)
  - "Peak + Accumulation", a **proxy-level** scoring formula for multi-turn attack detection. This is directly comparable to a sidecar-proxy design. [S] — [arXiv 2602.11247](https://arxiv.org/pdf/2602.11247)
  - SafeDream (safety world model for early detection). [S] — [arXiv 2604.16824](https://arxiv.org/pdf/2604.16824)
  - TRACE (trajectory-aware evaluation). [S] — [arXiv 2608.15594](https://arxiv.org/pdf/2608.15594)
- Crescendo, the canonical gradual-escalation multi-turn attack, appeared at USENIX Security 2025. [K] — [arXiv 2404.01833](https://arxiv.org/abs/2404.01833)
- Among the shipped guards: Llama Guard takes the conversation as context ([K] [arXiv 2312.06674](https://arxiv.org/abs/2312.06674)), and Qwen3Guard Gen's instructions include dialogue context. Neither model card reports a dedicated multi-turn attack benchmark. [V] — [LG4 card](https://huggingface.co/meta-llama/Llama-Guard-4-12B), [arXiv 2510.14276](https://arxiv.org/html/2510.14276v1)
- Encoder injection classifiers are single-segment classifiers with a 512-token window and no session state. [V] — [Prompt Guard 2 card](https://huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M)

### Inferences
- The over-defense profiles split into three groups:
  - "**Paranoid**": v1 Prompt Guard, deepset and fmops, which flag almost everything benign that contains trigger words.
  - "**Lexically-biased but moderate**": ProtectAI v2 and PIGuard, which are fine on general web text but flag 30-67% of agent tool outputs.
  - "**Low-FP by design**": Prompt Guard 2, Sentinel and Horizon-Labs.
  
  A student DeBERTa-v3-small model should be benchmarked against all three groups, and especially against Prompt Guard 2 22M, which is the closest in size (22M vs about 44M backbone for DeBERTa-v3-small).
- Over-defense rankings are **dataset-dependent**. ProtectAI v2 looks good on web pages and emails (0.5-1.2% FPR) but bad on AgentDojo (30.1%). So any over-defense claim needs several benign distributions, including structured inputs and tool outputs.
- No surveyed system reports FPR on **benign obfuscated or perturbed text**. Existing obfuscation work (Hackett et al., PIDS-Bench) perturbs only attacks. This is the clearest open gap for Paper 1.
- Multilingual guards with Hindi coverage (Prompt Guard 2 86M, Llama Guard 3/4, PolyGuard, Qwen3Guard) appear to evaluate script-native or machine-translated Hindi. **No source found evaluates romanized code-mixed Hinglish benign FPR.** This is a second clear gap for Paper 1.
- Prompt Guard 2 22M has no multilingual pretraining and a reported multilingual AUC of .942 versus .995 for 86M. That makes it likely to over-flag or under-detect Hinglish, but this has not been measured.
- Multi-turn session guarding is an active 2026 preprint area with mostly self-built datasets. No shipped injection classifier keeps session state. A sidecar proxy with session aggregation would be compared mainly to "Peak + Accumulation" (proxy-level), Defensive M2S and hierarchical-transformer approaches.

### Gaps
- Azure Prompt Shields: the current doc does not list supported languages and no FP rate is published. Older docs listed a language set, but it was not re-verified.
- Lakera Guard: no model size or architecture is public. The PINT dataset is proprietary and the repo is archived, so it cannot be independently reproduced.
- PromptShield (CODASPY 2025): per-detector TPR@low-FPR numbers were not retrieved; read the PDF.
- GenTel-Shield: parameter count and explicit FPR are not reported.
- NemoGuard JailbreakDetect: details were confirmed only via a third-party mirror.
- Rebuff and LLM Guard: no published FP benchmarks were found.
- Llama Guard 1/2/3 and WildGuard / ShieldGemma / Granite / Aegis basics are [K]. Verify the exact numbers in their cards before citing.
- PolyGuard head-to-head numbers and the exact 17-language list (one card table shows 15) were not verified.

---

## Key Question 2: Public benchmarks for injection/jailbreak detectors, and which measure benign false positives

### Takeaway
Most attack benchmarks measure only detection or attack success rate. Benign-FP measurement exists in four forms:
- Dedicated over-defense sets: NotInject, the PINT hard negatives, the PIDS-Bench hard-benign split, CAPTURE, XSTest, OR-Bench and PHTest.
- Utility under defense: AgentDojo utility and LlamaFirewall's "APR at 3% utility loss".
- Benign halves of jailbreak sets: JailbreakBench benign behaviors and WildJailbreak adversarial-benign.
- FPR on clean agent tool outputs.

None of these covers benign obfuscated text or code-mixed Hinglish.

### Cited Findings

**Benchmarks that explicitly measure benign false positives / over-defense**
- **NotInject** (339 benign sentences with 1-3 injection trigger words; 2024/ACL 2025) — [arXiv 2410.22770v3](https://arxiv.org/html/2410.22770v3) [V]
- **PINT** (Lakera): 4,314 inputs, of which 20.9% are hard negatives and about 94% are benign overall. It is multilingual (1,298 non-English inputs) and part-proprietary. — [PINT repo](https://github.com/lakeraai/pint-benchmark) [V]
- **PIDS-Bench** (IEEE Access 2026):
  - 43,172 instances in total.
  - Hard-benign split of 1,472: 872 externally sourced from LMSYS, OASST1 and Dolly, plus 600 curated.
  - Domain-shift (medical/legal/finance/code) and structural-shift (JSON wrapping, dilution, prefix mimicry) splits.
  - Obfuscation split of 405 attacks only.
  - Restricted to **English, single-turn**; multilingual and multi-turn are listed as future work.
  - Key finding: hard-negative augmentation "nearly eliminates over-defense on curated inputs but leaves externally sourced over-defense substantially intact". No internal operating point achieves F1≥0.95 with external FPR≤0.10.
  - [V] — [arXiv 2609.15017](https://arxiv.org/html/2609.15017)
- **CAPTURE** (LLMSec 2025): a context-aware benchmark covering both attacks and over-defense. — [arXiv 2505.12368](https://arxiv.org/pdf/2505.12368) [S]
- **PromptShield benchmark** (CODASPY 2025): conversational plus application-structured benign data, evaluated in the low-FPR regime. — [arXiv 2501.15145](https://arxiv.org/abs/2501.15145) [V abstract]
- **XSTest**: 250 safe prompts containing unsafe-sounding words and 200 unsafe contrast prompts; built for LLM over-refusal and reused for guards. — [arXiv 2308.01263](https://arxiv.org/abs/2308.01263) [K]; 250-safe count also in [AlphaSignal](https://alphasignal.ai/news/artificial-analysis-ranks-20-ai-safety-guards-and-wildguard-wins) [S]
- **OR-Bench**: about 80K seemingly-toxic benign prompts, a 1K hard subset and about 600 toxic prompts; built for LLM over-refusal. — [arXiv 2405.20947](https://arxiv.org/abs/2405.20947) [K]
- **PHTest** (pseudo-harmful prompts), used to measure guard over-refusal. — [arXiv 2409.00598](https://arxiv.org/abs/2409.00598) [K]; guard numbers in [arXiv 2609.33634](https://arxiv.org/html/2609.33634) [S]
- **WildGuardTest / WildJailbreak**: WildJailbreak includes *adversarial benign* prompts, which are contrastive benign items. — [arXiv 2406.18510](https://arxiv.org/abs/2406.18510), [arXiv 2406.18495](https://arxiv.org/abs/2406.18495) [K]
- **JailbreakBench (JBB-Behaviors)**: 100 harmful plus 100 benign behaviors. The benign half is used for over-refusal and guard FPR, as in Young 2025, who uses 200 harmful+benign behaviors. — [arXiv 2404.01318](https://arxiv.org/abs/2404.01318) [K]; usage [V] in [arXiv 2511.22047](https://arxiv.org/html/2511.22047v1)
- **CyberSecEval 2**: includes a textual prompt-injection test and a **False Refusal Rate** measure for borderline cybersecurity requests. — [arXiv 2404.13161](https://arxiv.org/abs/2404.13161) [K]
- **AgentDojo**: utility with and without attacks. Meta's guard metric is "APR at 3% utility reduction", which makes FP cost explicit. — [AgentDojo arXiv 2406.13352](https://arxiv.org/abs/2406.13352) [K]; metric [V] in [Prompt Guard 2 card](https://huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M). Clean-tool-output FPR is used in [arXiv 2610.03448](https://arxiv.org/html/2610.03448) [V]
- **WAInjectBench** (web agents) reports TPR and FPR for 12 detectors. — [arXiv 2510.01354](https://arxiv.org/pdf/2510.01354) [S]
- **GenTel-Bench**: 84,812 attacks, 1:1 benign. FP behaviour is visible only via precision. — [arXiv 2409.19521](https://arxiv.org/html/2409.19521v1) [V]

**Attack-only (or mostly attack) benchmarks**
- **BIPIA**: indirect injection on email, table, QA, code and summarization; train/test attack halves. — [arXiv 2312.14197](https://arxiv.org/abs/2312.14197) [K]; PIGuard's training contamination with BIPIA-train is documented in [arXiv 2610.03448](https://arxiv.org/html/2610.03448) [V]
- **InjecAgent**: about 1,054 indirect-injection cases over 17 user tools and 62 attacker tools. — [arXiv 2403.02691](https://arxiv.org/abs/2403.02691) [K]
- **HackAPrompt**: about 600K adversarial prompts from a competition. — [arXiv 2311.16119](https://arxiv.org/abs/2311.16119) [K]
- **TensorTrust**: about 126K hijacking and extraction attacks and about 46K defenses from an online game. — [arXiv 2311.01011](https://arxiv.org/abs/2311.01011) [K]
- **Multi-turn**: Crescendo [K] ([arXiv 2404.01833](https://arxiv.org/abs/2404.01833)); Scale AI MHJ multi-turn human jailbreaks [K] ([arXiv 2408.15221](https://arxiv.org/abs/2408.15221)); SafeDialBench and MTJ-Bench [S, named in search results] ([arXiv 2502.11090](https://arxiv.org/abs/2502.11090)).
- **Multilingual safety**: PolyGuardPrompts (17 languages, machine-translated) [S] ([arXiv 2504.04377](https://arxiv.org/pdf/2504.04377)); RTP-LX (used in Qwen3Guard) [V] ([arXiv 2510.14276](https://arxiv.org/html/2510.14276v1)); the multilingual toxicity guardrail benchmark (7 datasets, 10+ languages) [V] ([arXiv 2410.22153](https://arxiv.org/abs/2410.22153)).
- **Code-mixed perturbation attacks** (attack side only): ASR rose from 36.63% to 68.73% for phi-4B under code-mixing. [S] — [arXiv 2505.14469](https://arxiv.org/pdf/2505.14469)
- **Aggregators**: GuardBench (EMNLP 2024) aggregates about 40 safety datasets for guard evaluation, mostly content-harm. [K] — [ACL Anthology 2024.emnlp-main.1022](https://aclanthology.org/2024.emnlp-main.1022/)

### Inferences
- The benign side of every benchmark found is either:
  - English trigger-word sentences (NotInject, XSTest, OR-Bench, PHTest),
  - natural chat and documents (PINT, PIDS external), or
  - agent tool outputs (AgentDojo, τ-bench).

  None of them perturbs **benign** inputs with the same character-level transforms used in attacks, such as homoglyphs, leetspeak, zero-width characters or diacritics. None covers romanized code-mixed languages. A "NotInject-style" benign set with obfuscation and Hinglish slices would be novel.
- PIDS-Bench's finding that curated hard negatives do not transfer to externally sourced benign text matters for the team's own hard-negative retraining. In-distribution hard negatives may overstate over-defense fixes.

### Gaps
- Exact current sizes for XSTest, OR-Bench, HackAPrompt, TensorTrust, InjecAgent, CyberSecEval and JailbreakBench are [K]; verify them.
- SafeDialBench and MTJ-Bench details were not fetched.
- No benchmark measuring benign FPR on multi-turn conversations was found. Existing multi-turn sets measure attack detection.

---

## Key Question 3: Independent head-to-head evaluations of guard models and what they found about over-defense

### Takeaway
At least seven independent multi-guard comparisons exist from 2024 to 2026. They agree on four points:
1. Over-defense is large and highly distribution-dependent. Benign FPR ranges from 0% to over 90% across detectors on the same tool outputs.
2. Detection rankings do not transfer across benchmarks (Kendall τ of about 0.01 between BIPIA and AgentDojo).
3. Character-level obfuscation evades nearly every guard, with up to 100% ASR.
4. Results on public prompts overstate results on novel prompts, because of training contamination.

None of these studies evaluates multilingual/code-mixed over-defense or multi-turn sessions.

### Cited Findings
- **Liu (JAIST), "Passing the Test You Trained On", arXiv 2610.03448 (Oct 2026)**
  - Scope: 15 detectors plus 2 LLM judges on AgentDojo v1.2, τ-bench (+InjecAgent) and BIPIA.
  - Default-threshold FPR on benign tool outputs ranges from **0.0% to 93.1%**. ProtectAI v2 is at 30.1/66.9%, PIGuard at 29.5/11.0% and JasperLS at 78.5/93.1%. Prompt Guard 2, Sentinel, Wolf Defender and Horizon-Labs are at about 0-2%.
  - FP behaviour is **stable across agent benchmarks** (Kendall τ=0.67, p=0.001) but **not predicted by FPR on general text**.
  - Detection rankings do not transfer: BIPIA vs AgentDojo τ=0.01.
  - Documents training contamination for PIGuard (BIPIA, InjecAgent).
  - Does not cover multilingual, obfuscation or multi-turn.
  - [V] — [arXiv 2610.03448](https://arxiv.org/html/2610.03448)
- **Shire & Kim, PIDS-Bench, arXiv 2609.15017 / IEEE Access 2026**
  - Scope: TF-IDF, DistilBERT, DeBERTa-v3-FT, a regex reference, ProtectAI v2, DeBERTa-PI, Prompt Guard 2 86M and Llama Guard 3-1B.
  - A fine-tuned DeBERTa-v3 blocks 31.4% of external hard-benign prompts at τ=0.5. Its minimum attainable external FPR is 0.226.
  - Structural-shift FPRs are very high: DeBERTa-v3-FT 0.81, DeBERTa-PI 1.00.
  - Obfuscation recall: Prompt Guard 2 0.32, Llama Guard 3-1B 0.48, ProtectAI 0.906.
  - English, single-turn only.
  - [V] — [arXiv 2609.15017](https://arxiv.org/html/2609.15017)
  - Note: this is the closest prior work to the team's DeBERTa classifier and to Paper 1.
- **Hackett et al., "Bypassing LLM Guardrails", arXiv 2504.11168 (LLMSec 2025)**
  - Scope: 6 guards (Azure Prompt Shield, ProtectAI v1/v2, Meta Prompt Guard, NeMo Guard Jailbreak Detect, Vijil) against 12 character-injection techniques and 8 AML word-level attacks.
  - Emoji smuggling reached **100%** ASR on both PI and JB. Unicode tag smuggling reached 90.15/81.79%, numbers (leetspeak) 81.18/94.62%, and bidirectional text 78.69/99.23%.
  - White-box word-importance rankings transfer to black-box guards.
  - **Does not measure FP on benign perturbed text.**
  - [V] — [arXiv 2504.11168v3](https://arxiv.org/html/2504.11168v3)
- **Li et al., InjecGuard/PIGuard, arXiv 2410.22770 (ACL 2025)**
  - Scope: 8 baselines (fmops, deepset, PromptGuard, ProtectAIv2, Lakera, GPT-4o, Llama-2-chat, LlamaGuard3) on NotInject plus benign and malicious sets.
  - Open-source injection classifiers score 0.88-56.64% on NotInject, described as "close to random guessing levels (60%)" for the field. Detection and over-defense trade off; LlamaGuard3, for example, scores 99.7% on benign but 28.3% on malicious.
  - [V] — [arXiv 2410.22770v3](https://arxiv.org/html/2410.22770v3)
- **GenTel-Safe, arXiv 2409.19521 (Sept 2024)**
  - Scope: 7 detectors (ProtectAI, Hyperion, Prompt Guard, Lakera, Deepset, Fmops, WhyLabs LangKit).
  - Prompt Guard, Deepset and Fmops show about 50-61% precision on balanced sets, meaning they over-flag benign prompts.
  - Includes machine-translated multilingual evaluation.
  - [V] — [arXiv 2409.19521](https://arxiv.org/html/2409.19521v1)
- **Young, arXiv 2511.22047 (Nov 2025)**
  - Scope: 10 LLM safety guards on 1,445 prompts, including 500 OASST benign prompts and JBB-benign.
  - Implied benign FPR ranges from 0.6% (community LlamaGuard-7B) to about 36% (LlamaGuard-3-1B).
  - Accuracy on novel prompts collapsed for several models, for example Qwen3Guard-8B from 91.0 to 33.8.
  - Business-framed attacks had a 96.8% error rate across models.
  - English, single-turn only.
  - [V] — [arXiv 2511.22047](https://arxiv.org/html/2511.22047v1)
- **Lakera PINT leaderboard** (vendor-run, 2025): 8 systems, with PINT about 94% benign so that it weights FP heavily. [V] — [PINT](https://github.com/lakeraai/pint-benchmark)
- **Meta Prompt Guard 2 card / LlamaFirewall** (vendor-run): reports recall at 1% FPR and APR at 3% utility loss against ProtectAI, deepset and LLM Warden. [V] — [card](https://huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M); [S] [arXiv 2505.03574](https://arxiv.org/pdf/2505.03574)
- **Masked-diffusion guard paper, arXiv 2609.33634 (2026)**: WildGuard reached 77.03% on PHTest benign items, versus 94.80% for Llama Guard 3 and 93.21% for LG4. Qwen3Guard, WildGuard and Granite become "increasingly defensive as trigger cues accumulate". [S] — [arXiv 2609.33634](https://arxiv.org/html/2609.33634)
- **Artificial Analysis / NVIDIA guard ranking (20 guards, 7,232 prompts)**, per a secondary summary: WildGuard (89% F1), Qwen3Guard-8B (87%) and Nemotron 3.5 Content Safety (84%) sit on the quality-latency frontier. Llama Guard and ShieldGemma are the most permissive and Nemotron the most restrictive. [S, secondary] — [AlphaSignal](https://alphasignal.ai/news/artificial-analysis-ranks-20-ai-safety-guards-and-wildguard-wins)
  - This conflicts with arXiv 2609.33634 on WildGuard's over-refusal. Treat it as unresolved, since the two use different benchmarks.
- **Multilingual comparisons**:
  - Yang et al. (arXiv 2410.22153, Oct 2024) find guardrails "still ineffective at handling multilingual toxicity" and not robust to jailbreak prompts. [V abstract]
  - A related multilingual guardrail benchmark found one model had a high FPR on low-resource languages, over-classifying non-English prompts as unsafe. [S] — [OpenReview PDF](https://openreview.net/pdf/2d1048a5256a142487e36710ce84a9c7e675b79c.pdf)
- **CAPTURE** (LLMSec 2025): Fmops had 100% FNR and PromptGuard 100% FPR on context-aware data. InjecGuard and ProtectAIv2 had high FPR and FNR. [S] — [arXiv 2505.12368](https://arxiv.org/pdf/2505.12368)
- **WAInjectBench** (2025): across 12 detectors for web agents, PromptArmor and DataSentinel had the highest TPR with low FPR, and PromptGuard generalized poorly. [S] — [arXiv 2510.01354](https://arxiv.org/pdf/2510.01354)

### Inferences
- The strongest independent evidence says over-defense is (a) **distribution-specific** and (b) **not fixed by curated hard negatives**. Benign-FPR claims therefore need several held-out benign sources, ideally including the team's target distributions: obfuscated benign text and Hinglish.
- The evidence base on obfuscation is asymmetric. Attack-side evasion is well documented (Hackett 2025, PIDS-Bench), but the symmetric question, whether guards **over-flag benign text carrying the same perturbations**, is untested in every comparison found. This is a defensible novelty claim for Paper 1. Verify with a final targeted search before submission.
- Every head-to-head study found is English-centric, single-turn, or both. Paper 2 on multi-turn session guarding has no independent comparative baseline; the nearest are self-built-dataset preprints from 2026.
- Contamination findings, such as PIGuard on BIPIA and Qwen3Guard's collapse on novel prompts, suggest the team should report held-out, provenance-checked benign and attack splits.

### Gaps
- There is no independent head-to-head evaluation of guards on Hindi or Hinglish benign over-defense, and none on multi-turn benign FPR.
- The Artificial Analysis / NVIDIA guard benchmark primary source was not located; only the secondary news summary was seen.
- Full results tables for CAPTURE, WAInjectBench, PromptShield and the 2026 multi-turn preprints were not fetched; numbers are from snippets.
- The arXiv 2609.33634 and OpenReview multilingual-FPR claims are snippet-level and should be verified before citing.
