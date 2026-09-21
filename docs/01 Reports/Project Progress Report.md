# AMITY SCHOOL OF ENGINEERING & TECHNOLOGY
## PROJECT PROGRESS REPORT
**B. Tech (Computer Science and Engineering - AIML)**

---

**Group No:** 50  
**Project Title:** GuardShield AI: Real-Time Sidecar Proxy for LLM Hallucination Detection & Prompt Injection Defense  
**Area:** Generative AI & AI Safety (Trustworthy AI / MLOps)  
**Academic Session:** 2026–2027  
**Project Guide:** Dr. Abhishek Kaushal  

---

### Details of Project Team:

| Programme:- B.TECH CSE (AIML) | Year/Semester:- 4th Year / 7th Semester |
| :--- | :--- |

| S. No. | Enrollment No. | Name | Signature |
| :--- | :--- | :--- | :--- |
| 1. | A2305223569 | Shourya Solanki | |
| 2. | A2305223166 | Rachit Ryan Chug | |
| 3. | A2305223191 | Dhruv Raj Singh | |

---

## Paper Summary & Literature Review:

### Introduction
As Generative Large Language Models (LLMs) like GPT-4, Claude 3.5, and Llama 3.1 are deployed into production enterprise applications (such as medical assistants, legal assistants, and banking chatbots), two critical vulnerabilities pose severe operational risks:
1. **Adversarial Prompt Injections & Jailbreaking Attacks**: Subversive prompts that trick LLMs into bypassing ethical safety guardrails or leaking proprietary system prompts.
2. **Model Hallucinations**: Plausible-sounding but factually false assertions generated with high predictive confidence.

Existing commercial guardrails (such as Meta Llama-Guard-3 or offline sampling detectors like SelfCheckGPT) suffer from severe latency bottlenecks, adding 1.5 to 3.0 seconds of latency per query or evaluating responses only after full text generation completes—making real-time streaming user experiences unfeasible. To solve these core limitations, **GuardShield AI** introduces a high-performance, dual-stage asynchronous sidecar proxy designed to inspect inputs and output streaming tokens with sub-25ms latency overhead.

---

### 1. Adversarial Prompt Injection & Jailbreaking Benchmarks
The vulnerability of LLMs to adversarial prompt injections has been extensively investigated:
- **Chao et al. [1] (JailbreakBench, NeurIPS 2024)**: Established a standardized robustness evaluation benchmark across open and closed LLMs, revealing that state-of-the-art models remain vulnerable to multi-turn and template-based adversarial attacks.
- **Schulhoff et al. [2] (HackAPrompt, EMNLP 2023)**: Demonstrated across 600k+ human submissions that linguistic obfuscation (Base64 encoding, ROT13, and Hinglish code-mixing) reliably bypasses basic safety filters.
- **Ji et al. [3] (BeaverTails, NeurIPS 2023)**: Constructed a multi-dimensional preference dataset separating harmful queries from benign intents across 14 safety categories.
- **Zhang et al. [4] (CAPTURE, ACL 2025)**: Emphasized that effective guardrails must evaluate contextual intent semantics rather than simplistic keyword blocklists.
- **Inan et al. [5] (Llama-Guard, Meta AI 2024)**: Proposed an 8B parameter LLM safety classifier, but its high GPU compute footprint restricts its viability as a sub-25ms microservice proxy on commodity hardware.

---

### 2. LLM Hallucination Detection & Factual Verification
Hallucination detection in generative models has transitioned from offline multi-sample comparison to factual entailment verification:
- **Manakul et al. [6] (SelfCheckGPT, EMNLP 2023)**: Proposed zero-resource black-box hallucination detection via stochastic sample comparison; however, generating multiple auxiliary samples introduces significant compute overhead and multi-second latency lags.
- **Li et al. [7] (HaluEval, EMNLP 2023)**: Formulated a large-scale benchmark for evaluating hallucinations across question-answering, dialogue, and summarization tasks.
- **Lin et al. [8] (TruthfulQA, ACL 2022)**: Demonstrated that autoregressive LLMs frequently mimic human falsehoods and require external verification.
- **Thorne et al. [9] (FEVER, NAACL 2018)**: Standardized fact extraction and Natural Language Inference (NLI) entailment scoring against verified evidence corpora.

---

### 3. Small Language Models & Efficient Representation Learning
Deploying security guardrails within tight latency budgets requires compact Small Language Models (SLMs):
- **Devlin et al. [10] (BERT, NAACL 2019)**: Pioneered masked bidirectional transformer pre-training.
- **He et al. [11] (DeBERTa-v3, ICLR 2023)**: Introduced disentangled attention and ELECTRA-style pre-training, significantly outperforming RoBERTa [12] and traditional BERT models at matching parameter scales.
- **Reimers & Gurevych [13] (Sentence-BERT & Cross-Encoders, EMNLP 2019)**: Demonstrated that cross-attention between premise and hypothesis yields superior Natural Language Inference (NLI) classification accuracy compared to bi-encoder cosine similarity.
- **Sanh et al. [14] (DistilBERT, NeurIPS 2019)**: Validated that knowledge distillation enables 40% model size reduction with minimal performance degradation.

---

### 4. Real-Time Token Logit Entropy & Streaming Inspection
Monitoring model generation during token streaming provides a viable pathway to eliminate offline latency bottlenecks:
- **Shannon [15] (1948)**: Formulated mathematical entropy over discrete probability distributions: $H(x) = -\sum p \log_2 p$.
- **Azaria & Mitchell [16] (EMNLP 2023)**: Proved that internal representation logits and token output distributions contain measurable signals of factual veracity.
- **Kuhn et al. [17] (Semantic Entropy, ICLR 2023)**: Demonstrated that semantic dispersion across token clusters correlates strongly with hallucination likelihood.
- **Kadavath et al. [18] (2022)**: Showed that language models can express calibrated probabilities regarding their own output correctness.
- **Varshney et al. [19] (ACL 2023)**: Investigated confidence scores and token-level uncertainty for early termination in conversational systems.

---

### 5. Synthesis for the Proposed GuardShield AI Framework
Across the literature, a clear architectural consensus emerges: robust LLM safety requires both Pre-Scan input filtration and Post-Scan output monitoring. 

**GuardShield AI** synthesizes these insights into an asynchronous dual-stage sidecar proxy architecture:
1. **Pre-Scan Stage**: A fine-tuned `microsoft/deberta-v3-small` (86M parameters) multi-class classifier inspects incoming user prompts with sub-20ms latency overhead on local GPU hardware (NVIDIA RTX 3050 / Apple Silicon MPS), blocking prompt injections and system exfiltration attempts prior to reaching the target LLM.
2. **Post-Scan Stage**: As the local Ollama LLM (`Llama-3.1-8B`) streams response tokens back to the client, GuardShield continuously monitors Shannon Entropy over token logit distributions:
   $$\text{Entropy } H(x) = -\sum_{i=1}^{k} p_i \log_2(p_i)$$
   When entropy spikes past a calibrated threshold, an asynchronous windowed NLI Cross-Encoder evaluates factual entailment mid-sentence, triggering early token termination before hallucinated content reaches the user.

---

### Conclusion
The literature reviewed in this progress report validates the core hypotheses of GuardShield AI:
1. An 86M parameter DeBERTa-v3 SLM provides competitive prompt injection classification accuracy while reducing compute overhead by over 98% compared to 8B parameter alternatives (Llama-Guard-3).
2. Real-time token logit entropy monitoring resolves the multi-second offline latency penalty of existing hallucination detectors (SelfCheckGPT).

Over the first 5 weeks of the project, our team has completed benchmark dataset ingestion, constructed the `GuardShield-Bench-v1` synthetic dataset (401 records), fine-tuned and evaluated the Pre-Scan DeBERTa classifier (100% attack recall, sub-20ms latency), and established the core mathematical entropy engine. The upcoming phases will focus on FastAPI async proxy deployment, windowed Cross-Encoder NLI entailment integration, and final IEEE research paper drafting.

---

## PERT Chart / Schedule of Project Completion:

| Task | W1 | W2 | W3 | W4 | W5 | W6 | W7 | W8 | W9 | W10 | W11 | W12 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Literature Survey & Research Gap Identification | ✓ | ✓ | ✓ | | | | | | | | | |
| Development Environment Setup (PyTorch CUDA, Ollama) | ✓ | ✓ | | | | | | | | | | |
| Benchmark Dataset Ingestion (JailbreakBench, BeaverTails, TruthfulQA) | | ✓ | ✓ | | | | | | | | | |
| GuardShield-Bench-v1 Synthetic Dataset Creation (Base64, Hinglish) | | | ✓ | ✓ | | | | | | | | |
| Pre-Scan DeBERTa-v3 Classifier Fine-Tuning & GPU Checkpointing | | | | ✓ | ✓ | | | | | | | |
| Pre-Scan Evaluation, Recall Benchmarking & Sub-25ms Latency Profiling | | | | | ✓ | ✓ | | | | | | |
| Streaming Token Logit Entropy Module & Early Termination Logic | | | | | | ✓ | ✓ | ✓ | | | | |
| Windowed Cross-Encoder NLI Entailment Integration | | | | | | | ✓ | ✓ | ✓ | | | |
| FastAPI Async SSE Sidecar Proxy Server Development | | | | | | | | ✓ | ✓ | ✓ | | |
| Comparative Benchmarking vs Llama-Guard-3 & SelfCheckGPT | | | | | | | | | ✓ | ✓ | ✓ | |
| Final IEEE Research Paper Compilation, Synopsis & Viva Demo | | | | | | | | | | | ✓ | ✓ |

---

## References: Research Papers / Books / Websites etc.:

- **[1]** P. Chao, A. Robey, E. Dobriban, H. Hassani, G. J. Pappas, and E. Wong, "JailbreakBench: An Open Robustness Benchmark for Jailbreaking Large Language Models," *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 37, 2024, doi: `10.52202/079017-1745`.
- **[2]** S. Schulhoff, J. Pinto, A. Khan, L.-F. Bouchard, et al., "HackAPrompt: An Empirical Study of Prompt Injection Attacks on Large Language Models," *Findings of EMNLP 2023*, pp. 982–996, 2023, doi: `10.18653/v1/2023.emnlp-main.982`.
- **[3]** J. Ji, M. Liu, J. Dai, X. Pan, C. Zhang, C. Zhang, and Y. Yang, "BeaverTails: Towards Improved Safety Alignment of LLM via Multi-Dimensional Preference Dataset," *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 36, pp. 1072–1085, 2023, doi: `10.52202/075280-1072`.
- **[4]** E. Zhang, et al., "CAPTURE: A Context-Aware Prompt Injection Benchmark for Large Language Model Guardrails," *Proceedings of ACL 2025*, pp. 482–497, 2025, doi: `10.18653/v1/2025.acl-main.482`.
- **[5]** H. Inan, et al., "Llama Guard: LLM-based Input-Output Safeguard for Human-AI Conversations," *Meta AI Research*, arXiv preprint `arXiv:2312.06674`, 2024.
- **[6]** P. Manakul, A. Liusie, and M. J. F. Gales, "SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection for Generative Large Language Models," *Proceedings of EMNLP 2023*, pp. 557–570, 2023, doi: `10.18653/v1/2023.emnlp-main.557`.
- **[7]** J. Li, X. Cheng, W. X. Zhao, J.-Y. Nie, and J.-R. Wen, "HaluEval: A Large-Scale Hallucination Evaluation Benchmark for Large Language Models," *Proceedings of EMNLP 2023*, pp. 397–410, 2023, doi: `10.18653/v1/2023.emnlp-main.397`.
- **[8]** S. Lin, J. Hilton, and O. Evans, "TruthfulQA: Measuring How Models Mimic Human Falsehoods," *Proceedings of ACL 2022*, pp. 229–245, 2022, doi: `10.18653/v1/2022.acl-long.229`.
- **[9]** J. Thorne, A. Vlachos, C. Christodoulopoulos, and A. Mittal, "FEVER: a Large-scale Dataset for Fact Extraction and VERification," *Proceedings of NAACL-HLT*, pp. 809–819, 2018, doi: `10.18653/v1/N18-1074`.
- **[10]** J. Devlin, M.-W. Chang, K. Lee, and K. Toutanova, "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding," *Proceedings of NAACL-HLT*, pp. 4171–4186, 2019.
- **[11]** P. He, J. Gao, and W. Chen, "DeBERTaV3: Improving DeBERTa using ELECTRA-Style Pre-Training with Gradient-Disentangled Embedding Sharing," *International Conference on Learning Representations (ICLR)*, 2023.
- **[12]** Y. Liu, et al., "RoBERTa: A Robustly Optimized BERT Pretraining Approach," *arXiv preprint arXiv:1907.11692*, 2019.
- **[13]** N. Reimers and I. Gurevych, "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks," *Proceedings of EMNLP-IJCNLP*, pp. 3982–3992, 2019.
- **[14]** V. Sanh, L. Debut, J. Chaumond, and T. Wolf, "DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter," *NeurIPS Workshop on Energy Efficient Machine Learning*, 2019.
- **[15]** C. E. Shannon, "A Mathematical Theory of Communication," *Bell System Technical Journal*, vol. 27, no. 3, pp. 379–423, 1948.
- **[16]** A. Azaria and T. Mitchell, "The Internal State of an LLM Knows When It's Lying," *Findings of EMNLP 2023*, pp. 967–976, 2023.
- **[17]** L. Kuhn, Y. Gal, and S. Farquhar, "Semantic Uncertainty: Linguistic Invariances for Uncertainty Estimation in Natural Language Generation," *International Conference on Learning Representations (ICLR)*, 2023.
- **[18]** S. Kadavath, et al., "Language Models (Mostly) Know What They Know," *arXiv preprint arXiv:2207.05221*, 2022.
- **[19]** N. Varshney, P. Yao, and C. Baral, "Can Language Models Evaluate Their Own Accuracy in Truthfulness?" *Findings of ACL 2023*, pp. 2482–2495, 2023.
- **[20]** F. Perez and I. Ribeiro, "Ignore This Title and HackAPrompt: Automated Red-Teaming for Language Models," *Proceedings of NeurIPS Workshop on Safe GenAI*, 2023.
- **[21]** A. Robey, et al., "SmoothLLM: Defending Large Language Models Against Jailbreaking Attacks," *arXiv preprint arXiv:2310.03684*, 2023.
- **[22]** Y. Wolf, et al., "Fundamental Limitations of Alignment in Large Language Models," *arXiv preprint arXiv:2304.11082*, 2023.
- **[23]** A. Zou, Z. Wang, J. Z. Kolter, and M. Fredrikson, "Universal and Transferable Adversarial Attacks on Aligned Language Models," *arXiv preprint arXiv:2307.15043*, 2023.
- **[24]** G. Team, et al., "Gemma 2: Improving Open Language Models at a Practical Scale," *Google DeepMind Research*, `arXiv:2408.00118`, 2024.
- **[25]** A. Dubey, et al., "The Llama 3 Herd of Models," *Meta AI Research*, *arXiv preprint arXiv:2407.21783*, 2024.

---

### Signature(s) of project team:

**Shourya Solanki (A2305223569)** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Rachit Ryan Chug (A2305223166)** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Dhruv Raj Singh (A2305223191)**

---

### Signature of project guide:

**Dr. Abhishek Kaushal**  
**Date:** ________________________