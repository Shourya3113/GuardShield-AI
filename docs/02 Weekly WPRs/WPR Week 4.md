Format WPR

AMITY SCHOOL OF ENGINEERING & TECHNOLOGY
B.Tech (CSE - AIML) VII Semester

Project Area -- Generative AI & AI Safety (Trustworthy AI / MLOps)

Students Weekly Progress Report (WPR — Week 4) For Odd Semester of session 2026-2027

To be filled by Students:

| Field | Details |
| :--- | :--- |
| **Students Name** | 1. Shourya Solanki<br>2. Rachit Ryan Chug<br>3. Dhruv Raj Singh |
| **Roll no.** | 1. 01<br>2. 02<br>3. 03 |
| **Enrollment no.** | 1. A2305223569<br>2. A2305223166<br>3. A2305223191 |
| **Project Title finalized, if Yes, give name, if NO, give reason** | Yes. Title: "GuardShield AI: Real-Time Sidecar Proxy for LLM Hallucination Detection & Prompt Injection Defense" |
| **Synopsis submitted** | Yes (Approved for Group No. 50) |
| **Literature review** | Applied to model fine-tuning. Utilized cross-entropy loss and DeBERTa-v3 multi-class classification head for prompt injection detection. |
| **Technical & Economical Feasibility** | Feasible. Python 3.11+, PyTorch CUDA (RTX 3050 GPU), DeBERTa-v3-small (86M SLM), Hugging Face Trainer. Zero monetary cost (₹0). |
| **Bill of Material** | ₹0.00 (Fully open-source software stack and local developer environment) |
| **Project Progress Schedule (PERT Chart)** | • W1-W3: Setup, open-source dataset ingestion & GuardShield-Bench-v1 synthetic creation (Completed)<br>• W4-W7: DeBERTa-v3 model fine-tuning & evaluation pipeline (In Progress / Week 4)<br>• W8-W12: Token logit entropy algorithm, benchmark evaluation & IEEE paper draft |
| **Design of critical components** | 1. Pre-Scan DeBERTa-v3 Model Fine-Tuning Pipeline (`train_prescan.py`) <br>2. PyTorch Dataset Loader & Data Collator with Padding<br>3. Hugging Face Trainer Loop & Checkpointing (`models/deberta_v3_prescan/`) |
| **Fabrication work (give %)** | 0% (Software Project) |
| **Experimental work (give %)** | 45% (Pre-scan DeBERTa-v3 classifier fine-tuning script implemented, training pass executed on CUDA GPU, model checkpoints saved) |
| **Result and Analysis** | Configured PyTorch Trainer for microsoft/deberta-v3-small; executed fine-tuning on 320 train samples; verified loss convergence and checkpoint saving on CUDA GPU. |
| **Report writing** | WPR Week 4 drafted. |
| **Signature of students** | 1. Shourya Solanki &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 2. Rachit Ryan Chug &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 3. Dhruv Raj Singh |

Work done in this week (Week 4):
1. Pre-Scan Fine-Tuning Script Implementation: Developed `train_prescan.py` using PyTorch & Hugging Face `Trainer` to fine-tune `microsoft/deberta-v3-small` (86M SLM) on `train.json`.
2. Training Architecture & Loss Configuration: Configured sequence classification head (2 classes: Safe vs. Injection/Jailbreak), AdamW optimizer (learning rate 2e-5), and cross-entropy loss.
3. Training Execution on CUDA GPU: Executed fine-tuning on local NVIDIA GeForce RTX 3050 GPU, logging training loss across steps.
4. Model Checkpointing & Artifact Saving: Saved fine-tuned model weights and tokenizer configuration under `models/deberta_v3_prescan/`.

To be filled by Guide (strike off whichever is not applicable)
- Performance of students is satisfactory
- Performance of students is unsatisfactory
- A warning to be issued to student(s) (Name): ____________________
- Student was not well (Name): ____________________

Date: ____________________                                                              Signature of Guide: ____________________