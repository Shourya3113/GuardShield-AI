# Streaming / Entropy-Triggered Hallucination Detection and Lightweight NLI Grounding Verifiers

Scope: whether the student idea is novel and viable. The idea: during streaming generation, monitor per-token Shannon entropy over top-k logprobs. When entropy spikes for consecutive tokens, run a sentence-level NLI cross-encoder (currently zero-shot `cross-encoder/nli-deberta-v3-small`) against retrieved context mid-sentence, and terminate on contradiction. The claim is that this beats post-hoc detectors like SelfCheckGPT on latency. The team's current numbers: FEVER 86% accuracy; HaluEval-QA 60% accuracy, AUROC 0.61. The entropy circuit breaker has not been tested.

Research date: 2026-10-12. "Verified" means I read it this session in the paper, abstract or HTML, or in a primary model card or blog. "Search snippet" means it came from a search-engine summary and I did not open the primary page. "Not fetched" means a well-known arXiv ID cited from prior knowledge that I did not open this session; check it before quoting.

---

## Q1. How well does token-level uncertainty (raw entropy, semantic entropy, probes) predict hallucination?

### Takeaway
Raw token entropy and perplexity are weak to moderate hallucination predictors on long-form text, at about 0.65–0.76 AUC. They can be strong on short-form QA (up to about 0.94 on TriviaQA). Even sampling-based semantic entropy only averages about 0.79 AUROC on QA and drops to about 0.60–0.71 on long-form. Hidden-state probes beat all uncertainty baselines by a wide margin (0.85–0.90+ long-form). So entropy is a poor trigger for a detector that matters most on long-form RAG answers.

### Cited Findings
- **Most relevant head-to-head (Obeso, Arditi, Ferrando, Freeman, Holmes, Nanda, "Real-Time Detection of Hallucinated Entities in Long-Form Generation," arXiv 2509.03531, v2 Feb 2026).** Table 1 AUC numbers (verified):
  - **LongFact, Llama-3.1-8B / Llama-3.3-70B:** perplexity 0.760 / 0.706; token entropy 0.742 / 0.712; semantic entropy 0.719 / 0.714; linear probe 0.854 / 0.867; LoRA probe 0.894 / 0.905.
  - **HealthBench (held-out long-form):** entropy 0.665 / 0.647; semantic entropy 0.654 / 0.604; linear probe 0.856 / 0.873; LoRA probe 0.896 / 0.906.
  - **TriviaQA (short-form):** entropy 0.938 / 0.842; LoRA probe 0.965 / 0.983.
  - **MATH:** entropy 0.782 / 0.689; semantic entropy 0.852 / 0.793.
  - [arXiv HTML v2](https://arxiv.org/html/2509.03531v2)
- The Obeso et al. abstract headline is "AUC 0.90 vs 0.71 for Llama-3.3-70B" (probe vs semantic entropy, long-form). The paper evaluates four model families, up to 70B. — [arXiv abs](https://arxiv.org/abs/2509.03531)
- Obeso et al. limitations (verified):
  - The best LoRA probes reach only about 70% recall at 10% FPR on long-form.
  - The labeling pipeline had 80.6% recall and 15.8% FPR on injected errors.
  - Coverage is entity-level only, so relational and reasoning errors are not targeted.
  - [arXiv HTML v2](https://arxiv.org/html/2509.03531v2)
- **Semantic entropy (Farquhar, Kossen, Kuhn, Gal, Nature 2024).** The search-snippet summary says the average AUROC across 30 task–model combinations is 0.790 for semantic entropy, versus 0.691 for naive entropy, 0.698 for P(True) and 0.687 for embedding regression. I could not open the primary Nature page (paywall/redirect), so these are secondary figures to verify against the paper. — [Rubin Lake summary](https://rubinlake.com/en/technology-radar/ai-and-data-engineering/llm-evaluation-semantic-entropy); primary: [Nature](https://www.nature.com/articles/s41586-024-07421-0)
- **Semantic Entropy Probes (Kossen et al., arXiv 2406.15927).**
  - SE requires sampling multiple generations, which raises compute 5–10x.
  - SEPs predict SE from hidden states of a single generation, cutting the overhead to "almost zero."
  - SEPs generalize OOD better than accuracy probes.
  - The abstract page gives no AUROC figures.
  - [arXiv abs](https://arxiv.org/abs/2406.15927)
- **SelfCheckGPT paper (Manakul et al., EMNLP 2023), grey-box token baselines on WikiBio GPT-3 passages, sentence-level AUC-PR.** Columns are NonFact / NonFact* / Factual:
  - Avg(H) 80.73 / 37.09 / 52.07; Max(H) 85.75 / 32.43 / 50.27.
  - SelfCheckGPT-NLI 92.50 / 45.17 / 66.08 (random 72.96 / 29.72 / 27.04).
  - Entropy beats random but trails sampling-based consistency, especially on the hard NonFact* split.
  - [ar5iv](https://ar5iv.labs.arxiv.org/html/2303.08896)
- **Lookback Lens (Chuang et al., EMNLP 2024)** targets *contextual* hallucination, the RAG-relevant case. A linear classifier on per-head attention ratios (context vs generated tokens) is "as effective as" hidden-state or entailment-model detectors.
  - It transfers 7B→13B without retraining.
  - Classifier-guided decoding reduced XSum hallucination by 9.6%.
  - The snippet gives in-domain AUROC around 0.89–0.91 and about 0.66 in a sliding-window setting. This was read from a garbled table extraction, so verify against Table 2.
  - [arXiv 2407.07071](https://arxiv.org/html/2407.07071v2)
- A 2026 preprint argues entropy-based detection is hardest under greedy decoding: under sampling, hallucinated outputs have higher entropy partly by construction. — [arXiv 2605.28264](https://arxiv.org/html/2605.28264v1) (search snippet)
- A 2026 preprint ("Entropy Alone is Insufficient for Safe Selective Prediction in LLMs") reports SE as the strongest single method on TriviaQA/BioASQ. It notes SE needs K extra forward passes plus entailment. — [arXiv 2603.21172](https://arxiv.org/pdf/2603.21172) (search snippet)
- Other relevant internal-state / uncertainty methods. These are not fetched this session, with IDs from prior knowledge; all are offline and none is streaming-plus-NLI:
  - EigenScore/INSIDE (ICLR 2024) — [arXiv 2402.03744](https://arxiv.org/abs/2402.03744)
  - SAPLMA, "The Internal State of an LLM Knows When It's Lying" — [arXiv 2304.13734](https://arxiv.org/abs/2304.13734)
  - HaloScope (NeurIPS 2024) — [arXiv 2409.17504](https://arxiv.org/abs/2409.17504)
  - "LLM Internal States Reveal Hallucination Risk Faced With a Query" — [arXiv 2407.03282](https://arxiv.org/abs/2407.03282)
  - LN-entropy (length-normalized predictive entropy, Malinin & Gales) — [arXiv 2002.07650](https://arxiv.org/abs/2002.07650)

### Inferences
- A raw-entropy *trigger* with about 0.65–0.75 AUC on long-form means that at any useful threshold it will either miss a large share of hallucinations or fire constantly. Missed hallucinations never reach the NLI check, so system recall is capped by trigger recall. The team must report trigger recall separately from verifier accuracy.
- Hallucinations the model is *confident* about (low entropy) are invisible to the trigger. Contextual/RAG hallucinations, where the model fluently ignores retrieved context, are plausibly often low-entropy. That is why Lookback Lens uses attention, not entropy. This is inference, not a measured result.
- Top-k logprob entropy is a truncated approximation of full-vocabulary entropy. With API models (for example, k ≤ 20), the estimate is biased low. The team should state k and compare against full-vocab entropy on an open model. This is inference.

### Gaps
- I could not open the Nature semantic-entropy paper's primary tables; the 0.790/0.691 average AUROCs are secondary.
- I found no published AUROC for "entropy spike over N consecutive tokens" as a hallucination trigger specifically.

---

## Q2. Streaming, real-time and mid-generation detection and intervention: what exists?

### Takeaway
Streaming, token-level detection with early halting is now an active and crowded area. Examples:
- Hallucination: Obeso et al. probes with abstention; DRAD's entropy-triggered entity detection with retrieval.
- Safety: Qwen3Guard-Stream, SCM/FineHarm (NeurIPS 2025), Kelp/PlugGuard (ICML 2026), and hidden-state streaming probes (2026).

Uncertainty-triggered retrieval mid-decoding (FLARE, DRAD) is also established. The gap is narrow: none of these uses an *external NLI cross-encoder against retrieved context* as the verification step that the entropy trigger gates.

### Cited Findings
- **Obeso et al. streaming intervention.** On SimpleQA, the probe monitors every token; if any token score exceeds threshold t, generation halts and the model abstains.
  - Llama-3.3-70B without monitoring attempts about 80% of questions with under 30% conditional accuracy. Lowering t raises conditional accuracy while reducing attempts.
  - The hallucination reduction costs about 50% of correct answers.
  - Probes add "negligible computational overhead," running in the same forward pass.
  - [arXiv HTML v2](https://arxiv.org/html/2509.03531v2)
- **DRAD (Su et al., arXiv 2407.09417, "Mitigating Entity-Level Hallucination in LLMs").** Real-time Hallucination Detection (RHD) flags entities with low probability and high entropy, with no external models. Self-correction based on External Knowledge (SEK) then triggers retrieval and regenerates the flagged span. **This is the closest published precedent for "entropy-triggered mid-generation check plus retrieval."** — [arXiv 2407.09417](https://arxiv.org/abs/2407.09417v1); [code](https://github.com/oneal2000/EntityHallucination) (via search snippet)
- **FLARE (Jiang et al., 2023, "Active Retrieval Augmented Generation").** It generates a lookahead sentence; if it contains low-confidence (low-probability) tokens, it retrieves using it as a query and regenerates the sentence. It was evaluated on 4 long-form knowledge-intensive tasks. — [ar5iv 2305.06983](https://ar5iv.labs.arxiv.org/html/2305.06983)
- Not fetched; related decoding-time verification, all slower and multi-call, not streaming-halt:
  - Self-RAG (reflection tokens) — [arXiv 2310.11511](https://arxiv.org/abs/2310.11511)
  - Chain-of-Verification — [arXiv 2309.11495](https://arxiv.org/abs/2309.11495)
- **Qwen3Guard-Stream (0.6B/4B/8B, Apache-2.0, 119 languages).** It has token-level classification heads on a Qwen3 backbone and scores each assistant token. Its **debounce rule requires tokens i and i−1 both flagged before triggering**, which is the same "consecutive-token" idea the students use for entropy. — [HF model card](https://huggingface.co/Qwen/Qwen3Guard-Stream-0.6B); [Mozilla any-guardrail docs](https://docs.mozilla.ai/any-guardrail/api-reference/index/content-safety/qwen3-guard-stream); [tech report arXiv 2510.14276](https://arxiv.org/pdf/2510.14276v1)
- From a secondary review of the Qwen3Guard report:
  - Streaming loses about 2 points vs the generative guard.
  - About 86% exact sentence-level hit rate.
  - Near-linear scaling of processing time with response length.
  - [Moonlight review](https://www.themoonlight.io/en/review/qwen3guard-technical-report)
- **SCM / FineHarm (Li et al., NeurIPS 2025, "From Judgment to Interference").**
  - It argues that applying full-response moderators to partial outputs creates a training–inference mismatch. It also argues that re-encoding each prefix (as ProtectAI/GuardrailsAI-style partial detection does) adds redundant cost.
  - SCM reaches 0.95+ macro-F1, comparable to full detection, while seeing only the first 18% of tokens on average.
  - FineHarm has 29K pairs with token-level labels.
  - [arXiv 2506.09996](https://arxiv.org/pdf/2506.09996); [NeurIPS poster](https://neurips.cc/virtual/2025/poster/116186)
- **Kelp (arXiv 2510.09694; appears at ICML 2026 as "PlugGuard").** It is a plug-in head on the generator's hidden states with a temporal-consistency loss. The authors claim about 15.61% higher average F1 than post-hoc guards and earlier probes, about 20M parameters, and under 0.5 ms per token. It also introduces StreamGuardBench. — [arXiv 2510.09694](https://arxiv.org/pdf/2510.09694); [ICML 2026 poster](https://icml.cc/virtual/2026/poster/64082)
- **"Stop Early, Spend Less" (arXiv 2606.10487, June 2026).** Hidden-state probes in vLLM serve as a streaming surrogate for Qwen3Guard-Gen-8B.
  - Latency and size: the post-hoc guard adds about 480 ms per response, Qwen3Guard-Stream-8B adds about 40–54 ms on a second GPU, and the probe adds about 0.1 ms tail latency with about 8 MB of weights.
  - Early interruption: the probe interrupts about 92% of unsafe sequences within the first 20% of tokens.
  - Probing interval: probing every 2 steps costs about ±1 F1; an interval of 5 costs 3–6 F1.
  - Accuracy against human labels: the probe reaches F1 0.50 at the default threshold and 0.795 after tuning, versus about 0.85 for the guards.
  - [HF papers page](https://huggingface.co/papers/2606.10487)
- **Practitioner precedent (not peer-reviewed).** The "Director-AI" blog describes streaming middleware that buffers tokens, combines an NLI contradiction check with retrieval-based fact-checking, and cuts the LLM connection when a threshold is crossed. Treat its performance claims as unverified. — [dev.to](https://dev.to/anulum/system-architecture-deterministic-token-level-halting-for-llm-hallucinations-using-rust-and-2bc4)
- **HaluGate (vLLM blog, Dec 2025)** is a production hallucination gate: conditional verification (skip non-factual queries), token-level detection, and NLI explanation of unsupported claims. It appears to be request-level and post-hoc, not an entropy-gated streaming halt. — [vLLM blog](https://vllm.ai/blog/2025-12-14-halugate) (search snippet)

### Inferences
- The *components* are all published: entropy-triggered real-time detection (DRAD), low-confidence-triggered mid-generation retrieval (FLARE), consecutive-token debouncing (Qwen3Guard-Stream), streaming halt on detection (Obeso, SCM, Kelp), and NLI against retrieved evidence (SelfCheckGPT-NLI, HHEM, MiniCheck). The combination of an entropy gate, an NLI cross-encoder against retrieved context, and a mid-stream halt looks unpublished in peer-reviewed form. However, a reviewer is likely to see it as an incremental recombination, closest to DRAD with an NLI verifier swapped in for regeneration.
- The FineHarm "partial-output mismatch" argument applies directly. An NLI cross-encoder trained on complete hypotheses (MNLI/FEVER) is being fed *mid-sentence* fragments. Expect miscalibration unless the verifier is fine-tuned on prefixes. This is inference by analogy; I found no measurement of NLI on sentence prefixes.
- Probe-based streaming detectors (Obeso et al., Kelp, the 2026 probe paper) need white-box access. An entropy-plus-external-NLI design works with any API that exposes top-k logprobs and needs no training data. That black-box/grey-box, training-free angle is the most defensible differentiator. This is inference.

### Gaps
- I found no paper that measures NLI-verifier accuracy on partial (mid-sentence) hypotheses.
- I found no published false-stop-rate (benign-truncation) numbers for entropy-triggered halting.

---

## Q3. Lightweight grounding and factuality verifiers to compare against (size, latency, accuracy)

### Takeaway
Purpose-built grounding verifiers substantially outperform zero-shot MNLI/FEVER cross-encoders on RAG-style hallucination benchmarks:
- MiniCheck-FT5 (770M): 74.7% balanced accuracy on LLM-AggreFact, at GPT-4 level.
- LettuceDetect-large (ModernBERT, 8k ctx): 79.22% example-F1 on RAGTruth.
- HHEM-2.1-Open (T5-based): 74.3% balanced accuracy on RAGTruth-QA, under 1.5 s per 2k tokens on CPU.

The team's deberta-v3-small at 60% accuracy / 0.61 AUROC on HaluEval-QA is far below these and would be the weak point of any submission.

### Cited Findings
- **MiniCheck (Tang, Laban, Durrett, EMNLP 2024).** MiniCheck-FT5 (770M) reaches 74.7% balanced accuracy on LLM-AggreFact, vs GPT-4 75.3%. The authors claim GPT-4-level performance at 400x lower cost and 4–10% better accuracy than prior specialized checkers. The later Bespoke-MiniCheck-7B is listed at 77.4% on the leaderboard. — [arXiv 2404.10774](https://arxiv.org/html/2404.10774v2); [LLM-AggreFact benchmark page](https://www.alphaxiv.org/benchmarks/the-university-of-texas-at-austin/llm-aggrefact) (figures via search snippet)
- **AlignScore-Large (355M)** was the previous specialized state of the art, per a MiniCheck review. — [Liner review](https://liner.com/review/minicheck-efficient-factchecking-llms-on-grounding-documents) (search snippet); primary [arXiv 2305.16739](https://arxiv.org/abs/2305.16739) (not fetched)
- **LettuceDetect (KRLabs, arXiv 2502.17125).** It is a ModernBERT token classifier over (context, question, answer) with 8k context, giving span-level output. It reaches 79.22% example-level F1 on RAGTruth, 14.8% over Luna. It is about 30x smaller than the best LLM-based detectors and processes 30–60 examples/s on one GPU. — [arXiv 2502.17125](https://arxiv.org/html/2502.17125v1)
- **HHEM-2.1-Open (Vectara, T5-based).** Balanced accuracy is 76.55% on AggreFact-SOTA, 64.42% on RAGTruth-Summ and 74.28% on RAGTruth-QA (vs GPT-4 74.11%). Latency is under 1.5 s for 2k tokens on an Intel Xeon w7-3445 CPU. — [HF model card](https://huggingface.co/vectara/hallucination_evaluation_model); [Vectara blog](https://www.vectara.com/blog/hhem-2-1-a-better-hallucination-detection-model) (figures via search snippet / mirror)
- **Lynx (Patronus AI, arXiv 2407.08488).** These are a fine-tuned Llama-3-70B-Instruct and an 8B model, with HaluBench (15k samples). The authors claim it beats GPT-4o and Claude-3-Sonnet on HaluBench and is 8.3% more accurate than GPT-4o on PubMedQA. I could not confirm the exact overall accuracy. It is an LLM judge, so it is far heavier than cross-encoders. — [arXiv 2407.08488](https://arxiv.org/html/2407.08488v2); [Patronus blog](https://patronus.ai/blog/lynx-state-of-the-art-open-source-hallucination-detection-model)
- **SelfCheckGPT-NLI** uses DeBERTa-v3-large fine-tuned on MNLI, scoring by contradiction probability. — [ar5iv 2303.08896](https://ar5iv.labs.arxiv.org/html/2303.08896)
- Benchmarks reviewers expect for RAG grounding (not fetched this session):
  - RAGTruth (ACL 2024) — [arXiv 2401.00396](https://arxiv.org/abs/2401.00396)
  - LLM-AggreFact — [arXiv 2404.10774](https://arxiv.org/abs/2404.10774)
  - SummaC — [arXiv 2111.09525](https://arxiv.org/abs/2111.09525)
  - FActScore — [arXiv 2305.14251](https://arxiv.org/abs/2305.14251)
  - HaluBench — [arXiv 2407.08488](https://arxiv.org/html/2407.08488v2)

### Inferences
- The team's FEVER 86% does not transfer to HaluEval-QA (60% / 0.61 AUROC). That matches the general finding that FEVER/MNLI-trained cross-encoders under-perform on LLM-generated, multi-sentence, context-grounded claims. The natural fix is to swap in MiniCheck or HHEM-2.1-Open, or fine-tune on RAGTruth, before claiming anything. This is inference.
- LettuceDetect's span-level output is a better fit for streaming than a sentence-level NLI model. It could be run incrementally on growing prefixes, but its re-encoding cost per call must be measured. This is inference.

### Gaps
- I did not find per-call GPU latency for MiniCheck-FT5 or deberta-v3-small on comparable hardware; the team must measure these themselves.
- I did not confirm Lynx-70B's exact HaluBench accuracy.

---

## Q4. Is "entropy-triggered NLI verification mid-stream" already published? Closest competitors? Is SelfCheckGPT a fair latency baseline?

### Takeaway
I found no peer-reviewed paper with the exact combination. However, DRAD (entropy-triggered real-time entity detection plus retrieval), FLARE (low-confidence-triggered retrieval mid-generation), Obeso et al. (streaming token-level halt), and an unreviewed practitioner system (Director-AI, NLI plus retrieval streaming halt) cover it piecewise. **SelfCheckGPT is not a fair latency comparison.** It solves a different problem: zero-resource, black-box, no retrieved context, N=20 samples. Beating it on latency is trivial and reviewers will call it a strawman.

### Cited Findings
- **SelfCheckGPT setup.** It uses N=20 stochastic samples (temperature 1.0) per passage. The paper calls the Prompt variant "quite computationally heavy." Its API cost estimate for Yes/No prompting over 1,908 sentences × 20 samples was about $200 (GPT-3) or about $20 (ChatGPT). It is *zero-resource*: no external knowledge base. — [ar5iv 2303.08896](https://ar5iv.labs.arxiv.org/html/2303.08896)
- Closest competitors, with sources above:
  - DRAD/RHD — [arXiv 2407.09417](https://arxiv.org/abs/2407.09417v1)
  - FLARE — [ar5iv 2305.06983](https://ar5iv.labs.arxiv.org/html/2305.06983)
  - Obeso et al. streaming probes — [arXiv 2509.03531](https://arxiv.org/abs/2509.03531)
  - Lookback Lens with classifier-guided decoding — [arXiv 2407.07071](https://arxiv.org/html/2407.07071v2)
  - Director-AI (unreviewed) — [dev.to](https://dev.to/anulum/system-architecture-deterministic-token-level-halting-for-llm-hallucinations-using-rust-and-2bc4)
- Two extended web searches for "entropy-triggered / uncertainty-gated NLI verification during streaming with halt" returned no exact match. Both surfaced only partial matches (the items above, plus HaluGate). — [vLLM HaluGate](https://vllm.ai/blog/2025-12-14-halugate)
- Streaming moderation work has established "time-to-detection / fraction of tokens seen" as the latency metric:
  - SCM detects using the first 18% of tokens — [arXiv 2506.09996](https://arxiv.org/pdf/2506.09996)
  - The probe paper reports 92% interrupted within the first 20% of tokens and gives per-call ms costs — [HF 2606.10487](https://huggingface.co/papers/2606.10487)

### Inferences
- Fair latency and accuracy baselines for the same RAG setting:
  1. The same NLI verifier run post-hoc on every sentence. This is the crucial ablation, because it isolates what the entropy gate saves.
  2. The NLI verifier run on every sentence boundary while streaming, with no entropy gate.
  3. HHEM-2.1-Open, MiniCheck-FT5 and LettuceDetect, run post-hoc and per-sentence.
  4. DRAD/FLARE-style entropy triggers.
  5. If white-box, a linear probe (Obeso-style) or Lookback Lens.

  SelfCheckGPT can be included as a reference point but not as the headline comparison.
- The real claim to test is a Pareto one: NLI calls saved by gating versus recall lost through the gate. The headline number should be detection recall and F1 at a given verifier-call budget, plus time-to-detection in tokens. Wall-clock vs SelfCheckGPT is not the right headline.

### Gaps
- I could not access a full, recent survey enumerating all 2025–2026 streaming hallucination halting systems, so a closer unreviewed preprint may exist.

---

## Q5. Verdict: research contribution or system component? What evaluation would reviewers require?

### Takeaway
As currently specified (zero-shot small NLI at 0.61 AUROC, untested entropy gate, SelfCheckGPT as the latency foil), this is **better positioned as a system component** of the GuardShield pipeline than as a standalone research contribution. A publishable version would need:
1. A strong verifier (MiniCheck, HHEM or LettuceDetect level).
2. A rigorous gate-vs-no-gate Pareto analysis.
3. Prefix-robust verification.
4. Evaluation on RAGTruth plus a long-form benchmark against DRAD, FLARE and probe baselines.

The most defensible novelty angle is "training-free, grey-box (logprob-only) streaming grounding guard with measured compute savings."

### Cited Findings
- Strong reported baselines a reviewer will compare against:
  - Probes at about 0.85–0.90 AUC long-form vs entropy at about 0.65–0.74 — [arXiv 2509.03531](https://arxiv.org/html/2509.03531v2)
  - LettuceDetect 79.22% F1 on RAGTruth — [arXiv 2502.17125](https://arxiv.org/html/2502.17125v1)
  - MiniCheck 74.7% balanced accuracy on LLM-AggreFact — [arXiv 2404.10774](https://arxiv.org/html/2404.10774v2)
- Streaming-moderation papers at top venues (SCM at NeurIPS 2025, Kelp/PlugGuard at ICML 2026) required new token-level-labeled datasets/benchmarks (FineHarm, StreamGuardBench) plus early-detection metrics. That suggests the bar for streaming work includes a token- or prefix-level labeled evaluation set. — [arXiv 2506.09996](https://arxiv.org/pdf/2506.09996); [arXiv 2510.09694](https://arxiv.org/pdf/2510.09694)
- Benchmarks:
  - Long-form entity-level hallucination labels: LongFact, HealthBench — [arXiv 2509.03531](https://arxiv.org/html/2509.03531v2)
  - Span-level RAG hallucination labels: RAGTruth — [arXiv 2401.00396](https://arxiv.org/abs/2401.00396) (not fetched)
  - Atomic-fact long-form: FActScore — [arXiv 2305.14251](https://arxiv.org/abs/2305.14251) (not fetched)

### Inferences
- **Minimum evaluation reviewers would likely require (inference):**
  - **Benchmarks:** RAGTruth (span-level, real RAG outputs), plus at least one long-form set (FActScore bios, LongFact) and HaluEval/HaluBench for comparability. Avoid relying on FEVER, which is not LLM-generated text.
  - **Metrics:**
    - Trigger recall: the fraction of gold hallucinated spans that the entropy gate fires on.
    - End-to-end AUROC/F1.
    - Time-to-detection (tokens after the hallucinated span begins).
    - False-stop rate on faithful answers.
    - Number of NLI calls per response.
    - p50/p95 added latency on stated hardware.
  - **Ablations:**
    - Gate off (verify every sentence) vs gate on.
    - Entropy vs logprob vs probe as the gate.
    - Top-k size.
    - Consecutive-token window N and threshold.
    - Mid-sentence prefix vs sentence-boundary checks.
    - Verifier swap (deberta-v3-small vs MiniCheck vs HHEM).
  - **Baselines:** DRAD-RHD, FLARE-style trigger, post-hoc HHEM/MiniCheck/LettuceDetect, SelfCheckGPT (as reference only), and Lookback Lens or a linear probe if an open model is used.
  - **Multiple generator models** (at least 2 families), since entropy calibration varies by model and decoding temperature (see [arXiv 2605.28264](https://arxiv.org/html/2605.28264v1)).
- **For a security venue specifically (inference):** reviewers will ask about the *adversarial* setting. Can a prompt induce confident (low-entropy) hallucinations that bypass the gate, or poison retrieved context so NLI says "entailed"? A gate on entropy is trivially evaded by any attack that makes the model confident. Without an adaptive-attack evaluation, the security framing is weak. NLP venues (ACL/EMNLP Findings, or a workshop such as TrustNLP) are a more natural fit.
- **Viability as a system component (inference):** this is high, if the team (a) replaces the verifier with HHEM-2.1-Open or MiniCheck, (b) checks at sentence boundaries rather than mid-sentence unless prefix-robustness is shown, and (c) treats entropy as a cost-saving gate with a periodic unconditional check (for example, every k sentences) to bound the miss rate from low-entropy hallucinations.

### Gaps
- I found no published numbers on adversarial evasion of entropy-based hallucination triggers.
- I found no direct measurements of end-to-end latency for FLARE/DRAD-style mid-generation verification to benchmark against.
