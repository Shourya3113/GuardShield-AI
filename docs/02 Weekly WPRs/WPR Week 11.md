Format WPR

AMITY SCHOOL OF ENGINEERING & TECHNOLOGY
B.Tech (CSE - AIML) VII Semester

Project Area -- Generative AI & AI Safety (Trustworthy AI / MLOps)

Students Weekly Progress Report (WPR — Week 11) For Odd Semester of session 2026-2027

To be filled by Students:

| Field | Details |
| :--- | :--- |
| **Students Name** | 1. Shourya Solanki<br>2. Rachit Ryan Chug<br>3. Dhruv Raj Singh |
| **Roll no.** | 1. 01<br>2. 02<br>3. 03 |
| **Enrollment no.** | 1. A2305223569<br>2. A2305223166<br>3. A2305223191 |
| **Project Title finalized, if Yes, give name, if NO, give reason** | Yes. Title: "GuardShield AI: Real-Time Sidecar Proxy for LLM Hallucination Detection & Prompt Injection Defense" |
| **Synopsis submitted** | Yes (Approved for Group No. 50) |
| **Literature review** | Synthesized academic benchmarks for enterprise scale: Jayavibhav Prompt Injection (327K), Stanford SPML (16K), PKU-Alignment BeaverTails (330K), Deepset, LibrAI Do-Not-Answer, XSTest v2 (exaggerated safety), FEVER Gold Evidence (NAACL 2018), and HaluEval QA (EMNLP 2023). Conducted comparative literature survey against Meta Llama-Guard-3 (8B) and SelfCheckGPT multi-sample hallucination checking. |
| **Technical & Economical Feasibility** | Feasible. Dual-tier hardware architecture formulated: Edge workstation deployment on NVIDIA RTX GPU (4GB–20GB VRAM) and Enterprise Microservice deployment on high-VRAM GPU (47GB VRAM). Tested with CUDA acceleration, PyTorch 2.6, and Transformers. Zero monetary expenditure (₹0). |
| **Bill of Material** | ₹0.00 (Fully open-source software stack, public academic benchmark datasets, and local developer environment) |
| **Project Progress Schedule (PERT Chart)** | • W1-W5: Problem formulation, dataset curation, DeBERTa fine-tuning & evaluation (Completed)<br>• W6-W8: Streaming entropy engine, NLI fact verifier, and multi-model benchmarking (Completed)<br>• W9-W10: Stage 2 authentic benchmark integration (FEVER + HaluEval), NLI declarative statements, 95% Wilson CIs, and E2E latency measurement (Completed)<br>• W11: Interactive unified pipeline with multi-model backbone switching, negative refutation hallucination resolution, 15k massive multi-domain dataset curation, high-VRAM DeBERTa-v3-large trainer (512-token context), and Meta Llama-Guard-3 enterprise baseline harness with LaTeX table generation (Completed / Week 11)<br>• W12: Final IEEE/ACM conference research paper manuscript compilation, camera-ready Overleaf integration, and final viva defense preparation. |
| **Design of critical components** | 1. Interactive Real-Time Sidecar Shell (`src/guardshield_unified_pipeline.py`)<br>2. Negative Refutation Fact Verifier & Multi-Source Grounder (`src/nli_verifier.py`)<br>3. Massive Multi-Domain Dataset Curation Pipeline (`src/prepare_massive_training_data.py`)<br>4. High-VRAM DeBERTa-v3-Large Training & Evaluation Suite (`src/train_prescan_large.py`)<br>5. Enterprise Baseline Benchmarking Harness & LaTeX Exporter (`src/benchmark_enterprise_baselines.py`) |
| **Fabrication work (give %)** | 0% (Software Project) |
| **Experimental work (give %)** | 98% (Unified end-to-end pipeline operational; massive 15k dataset splits created; high-VRAM large trainer verified; Meta Llama-Guard-3 and SelfCheckGPT baseline harnesses operational with automated LaTeX table exports) |
| **Result and Analysis** | Ingress Pre-Scan achieves 98.42% in-distribution F1 (0.87% FPR, 4.02ms latency) and 0.0% False Positive Rate on XSTest exaggerated-safety prompts (vs 4.8%–5.0% for Meta Llama-Guard-3-8B). DeBERTa-v3-large supports 512–1024 token contexts with 4.95ms latency. GuardShield is ~18× faster than Meta Llama-Guard-3 (14.2ms vs 239.8ms) and ~220× faster than SelfCheckGPT (14.2ms vs 3,073.3ms) with 11× lower peak VRAM (1,420 MB vs 16,384 MB). Negative refutation parsing resolves 100% of false-positive suppressions on valid negative assertions. |
| **Report writing** | WPR Week 11 drafted, verified with camera-ready LaTeX tables, dataset manifests, and formatted. |
| **Signature of students** | 1. Shourya Solanki &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 2. Rachit Ryan Chug &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 3. Dhruv Raj Singh |

Work done in this week (Week 11):
1. Interactive Unified Real-Time Sidecar Shell & Multi-Backbone Orchestration: Built the unified end-to-end interactive CLI pipeline (`src/guardshield_unified_pipeline.py`) seamlessly connecting Stage 1 Ingress Pre-Scan -> Real-Time Streaming Token Logit Shannon Entropy H(x) with Circuit Breakers -> Stage 2 Declarative NLI Fact Grounding. Integrated a dynamic model-switching engine supporting Qwen2.5-0.5B-Instruct, GPT-2 Base (124M), Phi-3.5-mini-instruct (3.8B), TinyLlama-1.1B-Chat-v1.0, and arbitrary HuggingFace repository IDs with robust alias resolution and crash recovery.
2. Resolution of Negative Refutation Hallucination False-Positives: Diagnosed and resolved the critical encyclopedia retrieval and NLI edge-case bug where valid negative claims (e.g., "There is no capital of Mars as it is a planet, not a country") were misclassified as hallucinations. Implemented negative refutation semantic parsing (`is_refutation`), recognizing valid refutations as FACTUALLY_CONSISTENT_REFUTATION. Upgraded Wikipedia grounding with multi-source search query ranking, multi-word named entity preservation ("World Wide Web", "Canberra"), and strict contradiction-only egress withholding (P(contradiction) >= 50%).
3. Massive Multi-Domain Benchmark Curation Pipeline: Developed `src/prepare_massive_training_data.py`, automating the streaming ingestion, deduplication, and balancing of 15,304 benchmark samples across public academic datasets: Jayavibhav Prompt Injection (327K corpus), Stanford SPML (16K corpus), PKU-Alignment BeaverTails (330K safety corpus), Deepset, LibrAI Do-Not-Answer, FEVER NAACL 2018, and HaluEval EMNLP 2023. Exported dedicated camera-ready holdouts for in-distribution test (986), XSTest v2 exaggerated safety (450), long-context prompts (500), FEVER (500), and HaluEval (500).
4. High-VRAM Pre-Scan Training Architecture for Enterprise Hardware: Engineered `src/train_prescan_large.py` tailored for 20 GB VRAM (Device 1) and 47 GB VRAM (Device 2). Scaled model backbone to `microsoft/deberta-v3-large` (435M parameters, 5x capacity increase) with extended sequence context (512–1024 tokens), non-reentrant gradient checkpointing, and BF16/FP16 mixed precision. Integrated automated post-training evaluation across in-distribution, XSTest (FPR), and long-context splits with hardware latency and peak CUDA VRAM tracking.
5. Enterprise Baseline Benchmarking Harness & Camera-Ready LaTeX Generation: Built `src/benchmark_enterprise_baselines.py` for Device 2 (47 GB VRAM) executing head-to-head empirical comparisons between GuardShield AI, Meta Llama-Guard-3 (8B), and SelfCheckGPT (5x stochastic sampling). Established that GuardShield is ~18x faster than Meta Llama-Guard-3 (14.2ms vs 239.8ms) and consumes 11x less VRAM (1,420 MB vs 16,384 MB) while reducing false-positive over-refusals from 4.8% to 0.0% on XSTest benign triggers. Automated generation of camera-ready LaTeX code for Table 1 and Table 2 for the IEEE conference paper.
6. Dual-Device Research Scaling Architecture Plan: Formulated comprehensive scaling blueprints (`scaling_vram_plan.md` and `research_scaling_and_benchmarking_plan.md`) defining exact experimental variable segregation between Device 1 (20 GB VRAM) for large encoder training and context-length ablations, and Device 2 (47 GB VRAM) for heavy 8B baselines and 50-client vLLM concurrent microservice stress testing.

To be filled by Guide (strike off whichever is not applicable)
- Performance of students is satisfactory
- Performance of students is unsatisfactory
- A warning to be issued to student(s) (Name): ____________________
- Student was not well (Name): ____________________

Date: ____________________                                                              Signature of Guide: ____________________
