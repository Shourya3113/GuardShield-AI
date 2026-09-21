Format WPR

AMITY SCHOOL OF ENGINEERING & TECHNOLOGY
B.Tech (CSE - AIML) VII Semester

Project Area -- Generative AI & AI Safety (Trustworthy AI / MLOps)

Students Weekly Progress Report (WPR — Week 9) For Odd Semester of session 2026-2027

To be filled by Students:

| Field | Details |
| :--- | :--- |
| **Students Name** | 1. Shourya Solanki<br>2. Rachit Ryan Chug<br>3. Dhruv Raj Singh |
| **Roll no.** | 1. 01<br>2. 02<br>3. 03 |
| **Enrollment no.** | 1. A2305223569<br>2. A2305223166<br>3. A2305223191 |
| **Project Title finalized, if Yes, give name, if NO, give reason** | Yes. Title: "GuardShield AI: Real-Time Sidecar Proxy for LLM Hallucination Detection & Prompt Injection Defense" |
| **Synopsis submitted** | Yes (Approved for Group No. 50) |
| **Literature review** | Expanded to premier published research corpora: Stanford SPML Chatbot Injections (16K), Jayavibhav Prompt Injections (327K), Deepset Benchmark, ChatGPT JailbreakBench DAN Personas, FEVER NAACL 2018, and HaluEval EMNLP 2023 (35K). |
| **Technical & Economical Feasibility** | Feasible. Local NVIDIA GeForce RTX 3050 GPU (4GB VRAM), PyTorch 2.6 CUDA, Hugging Face Transformers, DeBERTa-v3 SLM (86M). Zero monetary cost (₹0). |
| **Bill of Material** | ₹0.00 (Fully open-source software stack and local developer environment) |
| **Project Progress Schedule (PERT Chart)** | • W1-W5: Setup, dataset curation, DeBERTa fine-tuning & evaluation (Completed)<br>• W6-W8: Streaming entropy engine, NLI grounding & comparative benchmarking (Completed)<br>• W9: Massive multi-dataset scaling (5,796 samples), Stanford SPML/Jayavibhav/HaluEval ingestion, local GPU fine-tuning, in-distribution & zero-shot OOD cross-benchmark validation (Completed / Week 9)<br>• W10-W12: IEEE research paper manuscript drafting, ablation experiments, and final project viva defense preparation. |
| **Design of critical components** | 1. Mega Benchmark Ingestion & Stratified Splitting Pipeline (`src/prepare_splits_v3_mega.py`)<br>2. Stage-1 DeBERTa-v3 High-Capacity GPU Training Engine (`src/train_prescan_v3.py`)<br>3. Multi-Benchmark Evaluation & Cross-Domain OOD Testing Suite (`src/evaluate_full_suite_v3.py`)<br>4. 3-Way Benchmark Progression Table & Dual Confusion Matrix Heatmaps |
| **Fabrication work (give %)** | 0% (Software Project) |
| **Experimental work (give %)** | 90% (Multi-benchmark scaling completed across 5,796 samples; established 98.71% in-distribution accuracy and 98.20% zero-shot OOD generalization) |
| **Result and Analysis** | Evaluated on 698 held-out test samples and 500 zero-shot OOD samples. Intercepts 98.03% of in-distribution attacks and 97.20% of novel jailbreaks with sub-11ms latency on RTX 3050 GPU; false positive rate suppressed to 0.58%. Stage 2 fact grounding intercepts 78.25% of hallucinations with 16.45ms latency. |
| **Report writing** | WPR Week 9 drafted. |
| **Signature of students** | 1. Shourya Solanki &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 2. Rachit Ryan Chug &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 3. Dhruv Raj Singh |

Work done in this week (Week 9):
1. Massive Multi-Dataset Ingestion (5,796 Total Samples): Following mentor guidance for upcoming research paper submission, expanded benchmarking from initial 451/1,182 samples to premier published research corpora: Stanford SPML Chatbot Injections (16K corpus), Jayavibhav Benchmark (327K corpus), Deepset Benchmark, ChatGPT JailbreakBench DAN Personas, FEVER NAACL 2018, and HaluEval EMNLP 2023.
2. Stratified Splitting & Out-of-Distribution (OOD) Pipeline: Partitioned the 5,000-sample security corpus into 70% Train (3,253 samples), 15% Validation (697 samples), and 15% Test (698 samples). Engineered a separate 500-sample zero-shot OOD test set featuring novel jailbreak vectors (DAN roleplay, base64 obfuscations, indirect injections) to rigorously test cross-dataset generalization.
3. Local GPU Model Fine-Tuning: Successfully fine-tuned `microsoft/deberta-v3-small` (86M parameters) across 3 epochs (612 steps) on local NVIDIA GeForce RTX 3050 GPU, achieving 98.28% validation accuracy and 0.9826 F1-score with 0.1024 validation loss.
4. Empirical Multi-Benchmark Results: Evaluated across held-out and OOD test splits, establishing:
   • In-Distribution Test (698 samples): 98.71% Accuracy, 98.03% Attack Recall (catches 348 of 355 attacks), 99.43% Precision, 0.58% False Positive Rate, and 10.10 ms median GPU latency.
   • Zero-Shot OOD Test (500 samples): 98.20% Accuracy, 97.20% Attack Recall (catches 243 of 250 novel jailbreak vectors), 99.18% Precision, and 12.04 ms latency.
   • Stage 2 Fact Grounding (648 samples): 75.31% Grounding Accuracy, 78.25% Contradiction Recall (catches 313 of 400 hallucinations), 81.09% Precision, and 16.45 ms latency.
5. Research Paper Deliverables & Visuals: Generated three empirical confusion matrices (`confusion_matrix_v3_in_distribution.png`, `confusion_matrix_v3_zero_shot_ood.png`, `confusion_matrix_v3_factuality.png`), compiled 3-Generation Progression LaTeX Table (`mega_benchmark_results_table.tex`), and updated the Google Colab demonstration suite.

To be filled by Guide (strike off whichever is not applicable)
- Performance of students is satisfactory
- Performance of students is unsatisfactory
- A warning to be issued to student(s) (Name): ____________________
- Student was not well (Name): ____________________

Date: ____________________                                                              Signature of Guide: ____________________
