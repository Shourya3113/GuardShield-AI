# GuardShield AI

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch 2.6](https://img.shields.io/badge/PyTorch-2.6-EE4C2C.svg)](https://pytorch.org/)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97-Transformers-yellow)](https://huggingface.co/)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Shourya3113/GuardShield-AI/blob/main/GuardShield_AI_Live_Colab_Suite.ipynb)

> **Real-Time Dual-Stage Pre-Scan Defense and Fact Grounding Architecture for Large Language Models**  
> *Capstone Research Project | Group 50 | Academic Year 2026*

---

## 📌 Executive Summary

Modern Large Language Models (LLMs) deployed in production environments face two critical, compounding vulnerability vectors:
1. **Adversarial Ingress**: Prompt injections, role-play jailbreaks, and obfuscated exploits that bypass system prompts to compromise model alignment.
2. **Hallucinatory Egress**: Fabricated assertions, unsupported extrapolations, and factual inconsistencies generated during open-ended decoding.

**GuardShield AI** provides a synchronous dual-stage defense pipeline combining:
- **Stage 1 (Pre-Scan Filter)**: A lightweight, fine-tuned transformer classifier (`microsoft/deberta-v3-small`: 44.3M backbone, 142.6M total parameters including the 128k SentencePiece vocabulary) that inspects ingress prompts in **~13.09 ms (p50)** with sliding-window chunking, blocking injections, jailbreaks, and length-padded attacks before they consume expensive downstream LLM decoding passes.
- **Stage 2 (Post-Generation Fact Grounding)**: A cross-encoder Natural Language Inference (NLI) verifier (`cross-encoder/nli-deberta-v3-small`) that performs premise-hypothesis entailment verification (**~13.89 ms p50**) to validate LLM assertions against authoritative retrieval context in RAG architectures.
- **Measured End-to-End Pipeline Latency**: Sequential Stage 1 + Stage 2 execution overhead measures **65.86 ms (p50)** / **68.47 ms (mean)** across 100 sequential queries on CUDA, logged per-sample in [`raw_eval_pipeline_e2e.json`](docs/01%20Reports/raw_eval_pipeline_e2e.json).

```mermaid
graph LR
    User([User Prompt]) --> PreScan[Stage 1: DeBERTa-v3 Pre-Scan Filter]
    PreScan -- "Malicious / Jailbreak (P >= 0.50)" --> Block[Blocked: 403 Forbidden]
    PreScan -- "Safe Prompt (P < 0.50)" --> LLM[Target Generative LLM]
    LLM --> Candidate[Generated Candidate Output]
    Candidate --> Stage2[Stage 2: Cross-Encoder NLI Verifier]
    Context[(Authoritative Context / RAG Docs)] --> Stage2
    Stage2 -- "Entailment (P_contra < 0.50)" --> Output([Verified Response to User])
    Stage2 -- "Contradiction (P_contra >= 0.50)" --> Flag[Hallucination Flagged / Blocked]
```

---

## 📊 V3 Mega Research Benchmark Evaluation (5,948 Curated Samples)

GuardShield AI has been empirically evaluated across **7 published academic and industry benchmark datasets**:
- **Security & Adversarial Benchmarks (5,148 samples)**:
  - *In-Distribution (4,648 samples)*: Partitioned into 3,253 Train, 697 Validation, and 698 Test samples across Stanford Online Safety (SPML), Jayavibhav Injection Suite, and Deepset Prompt Injections.
  - *Out-of-Distribution Zero-Shot (500 samples)*: 250 novel ChatGPT JailbreakBench attacks + 250 held-out benign queries.
- **Factuality & Hallucination Grounding Benchmarks (800 unique pairs)**:
  - 400 unique claim-evidence pairs from **FEVER (NAACL 2018)** (200 Supported, 200 Refuted).
  - 400 unique grounded-hallucinated QA pairs from **HaluEval (EMNLP 2023)** (200 Grounded, 200 Hallucinated).

### Empirical Evaluation Summary

| Defense Component | Evaluation Dataset / Split | Sample Size ($N$) | Accuracy (%) | Precision (%) | Recall (%) | F1-Score | FPR (%) | Median Latency (ms) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Stage 1: Pre-Scan** | **In-Distribution Test Split** | **698** | **98.42%** | **99.14%** | **97.75%** | **0.9844** | **0.87%** | **32.95 ms** |
| **Stage 1: Pre-Scan** | **Out-of-Distribution Zero-Shot** | **500** | **98.20%** | **98.79%** | **97.60%** | **0.9819** | **1.20%** | **18.48 ms** |
| **Stage 2: Fact Verifier** | **Multi-Source Fact Grounding (FEVER + HaluEval)** | **800** | **73.25%** | **76.88%** | **66.50%** | **0.7131** | **20.00%** | **18.91 ms** |
| **Dual-Stage Pipeline** | **Empirical Measured Sequential Overhead** | — | — | — | — | — | — | **65.86 ms** |

*Note: All Stage 1 metrics reflect pure neural inference with sliding-window chunking (no keyword heuristics). Stage 2 evaluates cross-encoder contradiction classification ($p_{\text{contradiction}} \ge 0.50$) across 800 authentic, non-duplicated academic benchmark pairs with declarative statement formulation: FEVER (86.50% Accuracy, 88.50% Recall, 15.50% FPR) and HaluEval QA (60.00% Accuracy, 44.50% Recall, 24.50% FPR). Complete prediction-level logs with per-sample scores and latencies are committed in `docs/01 Reports/raw_eval_*.json` for independent verification without GPU hardware.*

---

### Comparative Baseline: Transformer vs. Bag-of-Words (TF-IDF + Logistic Regression)

To assess whether the transformer representation provides genuine advantages over surface lexical features, we benchmarked a standard TF-IDF + Logistic Regression model against GuardShield on identical splits:

| Model Architecture | In-Distribution Accuracy | In-Distribution Recall | OOD Zero-Shot Accuracy | OOD Zero-Shot Recall | Generalization Delta |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **TF-IDF + Logistic Regression (Baseline)** | 94.56% | 91.55% | 80.00% | 62.40% | **-29.15% Recall Collapse** |
| **GuardShield DeBERTa-v3 (Ours)** | **98.42%** | **97.75%** | **98.20%** | **97.60%** | **-0.15% Robust Generalization** |

**Granular Zero-Shot OOD Generalization Breakdown**:
- **Authentic Human DAN Jailbreaks (76 prompts)**: On real, human-authored ChatGPT jailbreaks, GuardShield achieves **85.53% to 92.11% recall** (65 to 70 of 76 detected) against TF-IDF's **90.79%**. Because colloquial jailbreak prompts share explicit keyword markers (`"jailbroken"`, `"DAN"`, `"unfiltered"`), bag-of-words baselines detect them effectively.
- **Controlled Structural Template Shifts (174 prompts)**: Evaluated on 174 injection variations derived from 5 fixed structural templates with slot variations, TF-IDF drops to **50.00% recall**, while GuardShield's contextual transformer representation maintains **100.00% recall** (174 of 174 detected).
- **Overall OOD Attack Recall**: Across all 250 zero-shot attacks, GuardShield achieves **97.60% recall** (244 of 250) with a low false positive rate of **1.20%**.
- **In-Distribution Domain Breakdown**: Held-out in-distribution recall varies across provenance sources: Stanford SPML (**99.19%**, 301/303), Jayavibhav (**98.46%**, 128/130), and Deepset (**88.37%**, 38/43), reflecting natural cross-domain variability.
- **Statistical Rigor & Controls**: 95% Wilson score confidence intervals ($98.42\% \pm 0.96\%$), length-matched control experiments (length heuristic 60.61% vs. GuardShield 98.48%), and long-prompt sliding-window audits (66 prompts $\ge 200$ chars, 4.55% FPR) are detailed in [`statistical_rigor_and_controls.md`](docs/03%20Research%20and%20Catalogs/statistical_rigor_and_controls.md).

---

### 🛡️ Adaptive Adversarial Robustness & Evasion Defense

To evaluate robustness against advanced bypass vectors, GuardShield was benchmarked against 11 perturbation vectors on balanced cohorts ($N=100$ attacks, $N=100$ benign) with exact 95% Wilson confidence intervals (detailed in [`table_adaptive_robustness.md`](docs/01%20Reports/table_adaptive_robustness.md)):

1. **Adversarial Length-Padding Evasion Defense**:
   - **Benign Prefix Padding (>256 tokens prepended)**: Fixed 128-token truncation collapses to **0.0% recall** [0.0%, 3.7%]. GuardShield's sliding-window chunking maintains **98.0% recall** [93.0%, 99.45%] with **2.0% FPR** [0.55%, 7.0%].
   - **Sandwich Padding (benign prefix + suffix)**: Fixed truncation collapses to **0.0% recall** [0.0%, 3.7%]. GuardShield achieves **95.0% recall** [88.82%, 97.85%] with **2.0% FPR** [0.55%, 7.0%].
   - **Suffix Padding**: GuardShield achieves **94.0% recall** [87.52%, 97.22%] with **0.0% FPR** [0.0%, 3.7%].
2. **Disaggregated XSTest Evaluation ($N=450$)**:
   - **Safe Homonym Prompts ($N=250$)**: GuardShield achieves **0.0% False Refusal Rate (FRR)** [0.0%, 1.51%].
   - **Contrast Unsafe Prompts ($N=200$)**: Evaluated on direct toxic/harmful requests (non-injection), GuardShield achieves **0.0% block rate** [0.0%, 1.88%]. This confirms Stage 1's precise architectural specialization as a prompt-injection/jailbreak ingress filter, passing plain non-adversarial queries to upstream policy moderators.
3. **Probability Calibration**:
   - `PreScanSecurityFilter` incorporates temperature scaling ($T = 2.0$) to smooth cross-entropy logits, avoiding overconfident probability saturation on edge-case inputs.

---

## 🚀 Live Interactive Colab Suite

Experience GuardShield AI directly in Google Colab with free T4 GPU acceleration:  
👉 [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Shourya3113/GuardShield-AI/blob/main/GuardShield_AI_Live_Colab_Suite.ipynb)

The Colab suite includes 6 interactive modules:
1. **Environment Setup & GPU Telemetry**: Diagnostic verification of CUDA environment and PyTorch acceleration.
2. **Generative LLM Engine Selection**: Load and run test prompts through generative backbones including `Qwen/Qwen2.5-3B-Instruct`, `TinyLlama/TinyLlama-1.1B-Chat`, `microsoft/Phi-3.5-mini-instruct`, or `gpt2`.
3. **Stage 1 Neural Pre-Scan Filter**: Live prompt inspection and full in-distribution test-set evaluation without keyword overrides.
4. **Streaming Token Entropy Telemetry**: Real-time per-step token uncertainty profiling $H(x) = -\sum_{i=1}^k p_i \log_2(p_i)$ with automatic early-termination thresholding.
5. **Analytical Compute Savings Benchmark**: Analytical hardware profiling illustrating 94%–99.4% latency avoidance and 100% downstream decoding cost avoidance when intercepting attacks at Stage 1 before heavy 3B/7B autoregressive decoding passes.
6. **Stage 2 Fact Grounding & Interactive Defense Sandbox**: Live premise-hypothesis NLI verification and a unified sandbox for arbitrary user prompts.

---

## 📁 Repository Structure

```text
GuardShield_AI/
├── data/
│   ├── mega_research_datasets/   # Aggregated 5,148-sample security and 800 factuality benchmarks
│   ├── processed/splits_v3/       # Partitioned Train (3,253), Val (697), Test (698), OOD (500), and Fact (800)
│   ├── published_paper_datasets/  # Standardized benchmark CSVs from ACL, NAACL, EMNLP literature
│   └── raw/                       # Original ingested corpus samples
├── docs/
│   ├── 01 Reports/                # Academic progress reports, presentations, and confusion matrices
│   ├── 02 Weekly WPRs/            # Formal Weekly Progress Reports (WPR 1 through WPR 9)
│   ├── 03 Research and Catalogs/  # LaTeX tables, dataset catalogs, and research gap formulation
│   └── 04 Diagrams/               # System architecture and WBS diagrams
├── models/
│   ├── deberta_v3_prescan_v3/     # Fine-tuned Stage 1 model configs and evaluation summaries
│   └── README.md                  # Model weights reproduction and download guide
├── scripts/
│   ├── build_live_colab_suite.py  # Script generating the interactive Colab notebook
│   ├── build_wpr9.py              # Automated WPR document generation script
│   └── export_mega_datasets.py    # Master dataset export and validation utilities
├── src/
│   ├── config.py                  # Centralized path and hyperparameter configuration
│   ├── demo_master.py             # CLI demonstration suite for all pipeline components
│   ├── evaluate_full_suite_v3.py  # Pure neural benchmark test suite across in-dist, OOD, and factuality
│   ├── nli_verifier.py            # Stage 2 cross-encoder NLI entailment verifier
│   ├── prepare_splits_v3_mega.py  # V3 mega benchmark dataset partitioning pipeline
│   ├── prescan_filter.py          # Stage 1 real-time classification engine with sliding-window chunking
│   ├── proxy_server.py            # FastAPI sidecar proxy with modern lifespan management
│   ├── streaming_entropy_engine.py# Real-time token entropy calculation and spike detection
│   └── train_prescan_v3.py        # Stage 1 DeBERTa-v3-small GPU training script
├── GuardShield_AI_Live_Colab_Suite.ipynb  # Interactive Google Colab demonstration notebook
├── requirements.txt                       # Python project dependencies
├── LICENSE                                # Apache 2.0 Open Source License
└── README.md                              # Main project documentation
```

---

## 🛠️ Quickstart & Local Setup

### 1. Prerequisites & Installation
Ensure you have Python 3.10+ and a CUDA-compatible GPU (recommended):

```bash
git clone https://github.com/Shourya3113/GuardShield-AI.git
cd GuardShield-AI
pip install -r requirements.txt
```

### 2. Model Checkpoints & Pre-Trained Weights
Because binary model checkpoints exceed 500MB, they are not committed to git. Set them up via either option:

- **Option A (Train weights locally on your GPU in ~5 mins)**:
  ```bash
  python src/train_prescan_v3.py
  ```
- **Option B (Verify or download checkpoints using the weight manager)**:
  ```bash
  python scripts/download_weights.py
  ```
*(Note: Automated CI runs in lightweight verification mode using `GUARDSHIELD_ALLOW_UNTRAINED_FALLBACK=1`.)*

### 3. Run the Full V3 Benchmark Suite
Evaluate both Stage 1 and Stage 2 across in-distribution test sets, zero-shot out-of-distribution attacks, and factuality benchmarks:

```bash
python src/evaluate_full_suite_v3.py
```

### 4. Run the Sidecar Proxy Server
Launch the FastAPI sidecar proxy on `http://127.0.0.1:8000`:

```bash
python src/proxy_server.py
```

### 5. Interactive Command-Line Demonstration
Test custom prompts against the dual-stage defense in real-time:

```bash
python src/demo_master.py
```

---

## 📈 Weekly Project Progression

| Week | Phase / Milestone | Status | Key Deliverable |
| :---: | :--- | :---: | :--- |
| **W1** | Problem Statement & System Architecture Definition | ✅ Completed | WPR 1, Project Proposal, Baseline Design |
| **W2** | Literature Survey & Threat Model Characterization | ✅ Completed | WPR 2, Published Datasets Catalog |
| **W3** | Data Ingestion & Obfuscation Attack Synthesis | ✅ Completed | WPR 3, Processed Train/Val/Test Splits |
| **W4** | Stage 1 Model Training (`deberta-v3-small`) | ✅ Completed | WPR 4, Initial Pre-Scan Classifier |
| **W5** | Stage 2 Cross-Encoder NLI Verifier Integration | ✅ Completed | WPR 5, Premise-Hypothesis Pipeline |
| **W6** | Dual-Stage Pipeline Integration & Streaming Proxy | ✅ Completed | WPR 6, End-to-End Orchestrator |
| **W7** | Multi-Dataset Benchmarking (Stanford, Jayavibhav, Deepset) | ✅ Completed | WPR 7, 2,166-Sample Comparative Study |
| **W8** | Publication Preparation & Formal Research Catalogs | ✅ Completed | WPR 8, IEEE/ACM Ready LaTeX Tables |
| **W9** | V3 Mega Benchmark Scaling (5,948 Samples) & Colab Live Suite | ✅ Completed | WPR 9, 98.42% In-Dist Acc, 98.20% OOD Acc |
| **W10** | Authentic Stage 2 Benchmarks (FEVER/HaluEval), Statistical Controls, & Measured E2E Latency | ✅ Completed | WPR 10, 73.25% Grounding Acc, 65.86ms E2E p50, 95% Wilson CIs |

---

## 📚 Datasets & Attribution

GuardShield AI evaluates against open research datasets curated from the academic community:
- **Stanford Online Safety (SPML)**: [reshabhs/SPML_Chatbot_Prompt_Injection](https://huggingface.co/datasets/reshabhs/SPML_Chatbot_Prompt_Injection) (CC-BY-SA-4.0)
- **Jayavibhav Prompt Injection**: [jayavibhav/prompt-injection](https://huggingface.co/datasets/jayavibhav/prompt-injection) (Apache-2.0 / MIT)
- **Deepset Prompt Injections**: [deepset/prompt-injections](https://huggingface.co/datasets/deepset/prompt-injections) (Apache-2.0)
- **ChatGPT Jailbreak Prompts**: [rubend18/ChatGPT-Jailbreak-Prompts](https://huggingface.co/datasets/rubend18/ChatGPT-Jailbreak-Prompts) (MIT / Open Source)
- **FEVER Fact Extraction & VERification**: [copenlu/fever_gold_evidence](https://huggingface.co/datasets/copenlu/fever_gold_evidence) (Thorne et al., NAACL 2018, CC-BY-SA-3.0)
- **HaluEval Hallucination Benchmark**: [pminervini/HaluEval](https://huggingface.co/datasets/pminervini/HaluEval) (Wang et al., EMNLP 2023, MIT)
- **TruthfulQA**: [TruthfulQA](https://huggingface.co/datasets/truthful_qa) (Lin et al., ACL 2022, Apache-2.0)

---

## 👥 Research Team & Affiliation

**Capstone Project Group 50 | B.Tech (Computer Science & Engineering - AIML)**  
**Amity School of Engineering & Technology (ASET), Amity University**

- **Shourya Solanki** (Lead Architect — Pipeline Implementation, Model Training & Benchmarking)
- **Rachit Ryan Chug** (Research Analyst — Literature Survey, Gap Formulation & Verification)
- **Dhruv Raj Singh** (Data Engineer — Ingestion, Preprocessing & Corpus Curation)
- **Faculty Guide**: Dr. Abhishek Kaushal

---

## 📄 License

This repository is licensed under the [Apache License 2.0](LICENSE).
