Format WPR

AMITY SCHOOL OF ENGINEERING & TECHNOLOGY
B.Tech (CSE - AIML) VII Semester

Project Area -- Generative AI & AI Safety (Trustworthy AI / MLOps)

Students Weekly Progress Report (WPR — Week 5) For Odd Semester of session 2026-2027

To be filled by Students:

| Field | Details |
| :--- | :--- |
| **Students Name** | 1. Shourya Solanki<br>2. Rachit Ryan Chug<br>3. Dhruv Raj Singh |
| **Roll no.** | 1. 01<br>2. 02<br>3. 03 |
| **Enrollment no.** | 1. A2305223569<br>2. A2305223166<br>3. A2305223191 |
| **Project Title finalized, if Yes, give name, if NO, give reason** | Yes. Title: "GuardShield AI: Real-Time Sidecar Proxy for LLM Hallucination Detection & Prompt Injection Defense" |
| **Synopsis submitted** | Yes (Approved for Group No. 50) |
| **Literature review** | Applied to latency benchmarking and inference optimization. Verified DeBERTa-v3 sub-25ms pre-scan latency constraint on test split. |
| **Technical & Economical Feasibility** | Feasible. Python 3.11+, PyTorch CUDA (RTX 3050 GPU), DeBERTa-v3 SLM (86M params), standalone inference engine. Zero monetary cost (₹0). |
| **Bill of Material** | ₹0.00 (Fully open-source software stack and local developer environment) |
| **Project Progress Schedule (PERT Chart)** | • W1-W3: Setup, open-source dataset ingestion & GuardShield-Bench-v1 synthetic creation (Completed)<br>• W4-W7: DeBERTa-v3 model fine-tuning & evaluation pipeline (In Progress / Week 5)<br>• W8-W12: Token logit entropy algorithm, benchmark evaluation & IEEE paper draft |
| **Design of critical components** | 1. Pre-Scan Model Evaluation Script (`evaluate_prescan.py`)<br>2. Pre-Scan Security Filter Engine (`prescan_filter.py`)<br>3. Quantitative Accuracy & Latency Metrics Pipeline |
| **Fabrication work (give %)** | 0% (Software Project) |
| **Experimental work (give %)** | 55% (Pre-scan evaluation executed on 41 test samples, accuracy and F1 metrics calculated, sub-25ms inference latency verified on CUDA GPU, standalone filter engine implemented) |
| **Result and Analysis** | Evaluated fine-tuned DeBERTa-v3 on test.json; confirmed 87.8% Accuracy and sub-20ms average inference latency on CUDA GPU, meeting real-time sidecar requirements. |
| **Report writing** | WPR Week 5 drafted. |
| **Signature of students** | 1. Shourya Solanki &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 2. Rachit Ryan Chug &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 3. Dhruv Raj Singh |

Work done in this week (Week 5):
1. Model Evaluation Pipeline Implementation: Developed `evaluate_prescan.py` to benchmark the fine-tuned `microsoft/deberta-v3-small` classifier across 41 test samples from `test.json`.
2. Performance & Metrics Quantification: Measured Classification Accuracy, Precision, Recall, and F1-Score on prompt injection and adversarial test prompts.
3. Latency Benchmarking on CUDA GPU: Benchmarked per-request inference overhead on local NVIDIA GeForce RTX 3050 GPU, confirming sub-20ms latency (within the sub-25ms real-time constraint).
4. Standalone Security Filter Module: Implemented `src/prescan_filter.py` providing a production-ready interface returning safety decision (ALLOW/BLOCK), risk score, and execution latency in milliseconds.

To be filled by Guide (strike off whichever is not applicable)
- Performance of students is satisfactory
- Performance of students is unsatisfactory
- A warning to be issued to student(s) (Name): ____________________
- Student was not well (Name): ____________________

Date: ____________________                                                              Signature of Guide: ____________________