Format WPR

AMITY SCHOOL OF ENGINEERING & TECHNOLOGY
B.Tech (CSE - AIML) VII Semester

Project Area -- Generative AI & AI Safety (Trustworthy AI / MLOps)

Students Weekly Progress Report (WPR — Week 3) For Odd Semester of session 2026-2027

To be filled by Students:

| Field | Details |
| :--- | :--- |
| **Students Name** | 1. Shourya Solanki<br>2. Rachit Ryan Chug<br>3. Dhruv Raj Singh |
| **Roll no.** | 1. 01<br>2. 02<br>3. 03 |
| **Enrollment no.** | 1. A2305223569<br>2. A2305223166<br>3. A2305223191 |
| **Project Title finalized, if Yes, give name, if NO, give reason** | Yes. Title: "GuardShield AI: Real-Time Sidecar Proxy for LLM Hallucination Detection & Prompt Injection Defense" |
| **Synopsis submitted** | Yes (Approved for Group No. 50) |
| **Literature review** | Applied to synthetic dataset design. Incorporated Base64, ROT13, and Hinglish adversarial obfuscation attack vectors. |
| **Technical & Economical Feasibility** | Feasible. Python 3.11+, PyTorch CUDA (RTX 3050 GPU), DeBERTa-v3-small (86M SLM), Hugging Face Trainer. Zero monetary cost (₹0). |
| **Bill of Material** | ₹0.00 (Fully open-source software stack and local developer environment) |
| **Project Progress Schedule (PERT Chart)** | • W1-W3: Setup, open-source dataset ingestion & GuardShield-Bench-v1 synthetic creation (Completed / Week 3)<br>• W4-W7: DeBERTa-v3 model fine-tuning & preprocessing pipeline<br>• W8-W12: Token logit entropy algorithm, benchmark evaluation & IEEE paper draft |
| **Design of critical components** | 1. Obfuscated Synthetic Dataset Generator (Base64/ROT13/Hinglish)<br>2. Dataset Splitting Pipeline (80% Train, 10% Val, 10% Test)<br>3. Pre-Scan DeBERTa-v3 Multi-Class Classifier Initialization |
| **Fabrication work (give %)** | 0% (Software Project) |
| **Experimental work (give %)** | 35% (Synthetic dataset generation, 401 records created, 80/10/10 split prepared, DeBERTa-v3 GPU initialization verified) |
| **Result and Analysis** | Generated GuardShield-Bench-v1 (401 synthetic obfuscated records); created train (320), val (40), test (41) splits; verified DeBERTa-v3 forward-pass on CUDA GPU. |
| **Report writing** | WPR Week 3 drafted. |
| **Signature of students** | 1. Shourya Solanki &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 2. Rachit Ryan Chug &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 3. Dhruv Raj Singh |

Work done in this week (Week 3):
1. GuardShield-Bench-v1 Synthetic Dataset Creation: Built `obfuscation_generator.py` applying Base64, ROT13, and Hinglish code-mixing to benchmark prompt injections, producing 401 standardized records.
2. Train/Val/Test Dataset Splitting: Implemented `prepare_splits.py` dividing dataset into 80% Train (320 items), 10% Validation (40 items), and 10% Test (41 items) under `data/processed/splits/`.
3. DeBERTa-v3 Model Initialization: Developed `model_init.py` initializing Hugging Face `microsoft/deberta-v3-small` (86M parameters) on local NVIDIA RTX 3050 CUDA GPU.
4. Baseline Forward-Pass Verification: Tested model tokenizer and classification logits, confirming pipeline readiness for fine-tuning.

To be filled by Guide (strike off whichever is not applicable)
- Performance of students is satisfactory
- Performance of students is unsatisfactory
- A warning to be issued to student(s) (Name): ____________________
- Student was not well (Name): ____________________

Date: ____________________                                                              Signature of Guide: ____________________