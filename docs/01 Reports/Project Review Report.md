# AMITY SCHOOL OF ENGINEERING & TECHNOLOGY
## PROJECT PROGRESS REPORT
**B. Tech (Computer Science and Engineering - AIML) | 4th Year / 7th Semester**
**Academic Session:** 2026–2027

---

**Group No.:** 50  
**Project Title:** GuardShield AI: Real-Time Sidecar Proxy for LLM Hallucination Detection & Prompt Injection Defense  
**Project Area:** Generative AI & AI Safety (Trustworthy AI / MLOps)  
**Project Guide:** Dr. Abhishek Kaushal  
**Institution:** Amity School of Engineering & Technology (ASET), Amity University  

---

### Project Team Details:

| Programme | Semester |
| :--- | :--- |
| B.TECH CSE (AIML) | 4th Year / 7th Semester (Odd 2026-2027) |

| S. No. | Enrollment No. | Student Name & Project Role | Signature |
| :--- | :--- | :--- | :--- |
| 1. | A2305223569 | Shourya Solanki (Lead Architect — Pipeline Implementation & Benchmarking) | |
| 2. | A2305223166 | Rachit Ryan Chug (Research Analyst — Literature Survey & NLI Formulation) | |
| 3. | A2305223191 | Dhruv Raj Singh (Data Engineer — Multi-Corpus Curation & Preprocessing) | |

---

## 1. Executive Summary & Problem Formulation

Modern Large Language Models (LLMs) deployed across high-stakes domains (healthcare, legal counsel, autonomous agent workflows, and financial services) suffer from two compounding, catastrophic failure modes:
1. **Adversarial Ingress Attacks**, where malicious users craft direct prompt injections, jailbreaks, and obfuscated payload wrappers that bypass system instructions.
2. **Hallucinatory Egress Generation**, where autoregressive models emit plausible-sounding but factually ungrounded assertions with high predictive confidence.

Existing commercial safety guardrails exhibit severe operational trade-offs. Heavy LLM-based classifiers such as Meta Llama-Guard-3 (8B parameters) impose between 1,500 ms and 3,500 ms of latency per query, rendering them unfeasible for sub-second production microservices. Conversely, post-generation factual consistency detectors (e.g., SelfCheckGPT) rely on stochastic multi-sample generation, compounding inference costs and introducing multi-second offline bottlenecks.

**GuardShield AI** introduces a high-throughput, low-latency dual-stage sidecar proxy architecture combining:
- **Stage 1 (Pre-Scan Filter)**: Fine-tuned `microsoft/deberta-v3-small` (44.3M backbone, 142.6M total params) intercepting prompt injections in ~13.09 ms (p50) with sliding-window chunking.
- **Dynamic Streaming Shannon Entropy Engine**: Halts generation mid-sentence when sustained uncertainty spikes occur.
- **Stage 2 (Cross-Encoder NLI Fact Grounding)**: Validates generated assertions against authoritative retrieval context in ~13.89 ms (p50).

---

## 2. Empirical Multi-Benchmark Evaluation Results (5,948 Samples)

| Evaluation Benchmark | Dataset Source(s) | Sample Count | Accuracy (%) | Recall (%) | Precision (%) | FPR (%) | Median Latency |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Stage 1 In-Distribution Test** | Stanford SPML + Jayavibhav + Deepset | 698 held-out | **98.42% ± 0.96%** | 97.75% (347/355) | 99.14% | 0.87% (3/343) | 32.95 ms (p50) |
| **Stage 1 Zero-Shot OOD Generalization** | ChatGPT JailbreakBench + Benign | 500 unseen | **98.20% ± 1.22%** | 97.60% (244/250) | 98.79% | 1.20% (3/250) | 18.48 ms (p50) |
| **Scientific Length-Matched Control** | Length-Controlled Balanced Split | 198 control | **98.48%** (Length: 60.61%) | 96.97% | 100.00% | 0.00% | 24.12 ms (p50) |
| **Long Safe Prompt False-Positive Audit** | Academic Technical Queries (>= 200 chars) | 66 long prompts | **95.45% Pass Rate** | -- | -- | 4.55% (3/66) | 36.65 ms (p50) |
| **Stage 2 Authentic Fact Grounding** | FEVER (NAACL) + HaluEval (EMNLP) | 800 unique pairs | **73.25% ± 3.06%** | 66.50% (FEVER: 88.5%) | 76.88% | 20.00% | 18.91 ms (p50) |
| **Sequential End-to-End Pipeline (CUDA)** | Combined Stage 1 + Stage 2 Sequential | 100 real queries | -- | -- | -- | -- | **65.86 ms (p50)**<br>Mean: 68.47 ms |

---

## 3. Defense Efficiency & Compute Savings

- **GPT-2 (124M)**: Unprotected latency = 175.4 ms vs GuardShield = 12.87 ms (92.66% latency reduction; 48 tokens saved).
- **TinyLlama-1.1B**: Unprotected latency = 740.2 ms vs GuardShield = 12.87 ms (98.26% latency reduction; 65 tokens saved).
- **Qwen2.5-3B-Instruct**: Unprotected latency = 1,850.6 ms vs GuardShield = 12.87 ms (99.30% latency reduction; 92 tokens saved).
- **Qwen2.5-7B-Instruct**: Unprotected latency = 3,420.0 ms vs GuardShield = 12.87 ms (99.62% latency reduction; 120 tokens saved).

---

## 4. Signatures

**Project Team Members:**  
Shourya Solanki (A2305223569) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Rachit Ryan Chug (A2305223166) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Dhruv Raj Singh (A2305223191)  

**Project Guide:**  
Dr. Abhishek Kaushal  
Faculty Guide, Dept. of Computer Science & Engineering  
Amity School of Engineering & Technology (ASET)  
Date: ________________________  
