Format WPR

AMITY SCHOOL OF ENGINEERING & TECHNOLOGY
B.Tech (CSE - AIML) VII Semester

Project Area -- Generative AI & AI Safety (Trustworthy AI / MLOps)

Students Weekly Progress Report (WPR — Week 7) For Odd Semester of session 2026-2027

To be filled by Students:

| Field | Details |
| :--- | :--- |
| **Students Name** | 1. Shourya Solanki<br>2. Rachit Ryan Chug<br>3. Dhruv Raj Singh |
| **Roll no.** | 1. 01<br>2. 02<br>3. 03 |
| **Enrollment no.** | 1. A2305223569<br>2. A2305223166<br>3. A2305223191 |
| **Project Title finalized, if Yes, give name, if NO, give reason** | Yes. Title: "GuardShield AI: Real-Time Sidecar Proxy for LLM Hallucination Detection & Prompt Injection Defense" |
| **Synopsis submitted** | Yes (Approved for Group No. 50) |
| **Literature review** | Applied to windowed NLI factual entailment verification. Linked Cross-Encoder premise-hypothesis scoring with streaming entropy spikes. |
| **Technical & Economical Feasibility** | Feasible. Python 3.11+, PyTorch CUDA (RTX 3050), Cross-Encoder NLI, FastAPI async SSE proxy. Zero monetary cost (₹0). |
| **Bill of Material** | ₹0.00 (Fully open-source software stack and local developer environment) |
| **Project Progress Schedule (PERT Chart)** | • W1-W5: Setup, dataset curation, DeBERTa fine-tuning & evaluation (Completed)<br>• W6-W8: Streaming entropy engine, NLI verification & async proxy server (In Progress / Week 7)<br>• W9-W12: Comparative benchmarking vs Llama-Guard & final IEEE research paper |
| **Design of critical components** | 1. Windowed Cross-Encoder NLI Entailment Verifier (`nli_verifier.py`)<br>2. Dual-Stage End-to-End Pipeline Integration (`guardshield_pipeline.py`)<br>3. Factual Grounding & Hallucination Contradiction Scoring |
| **Fabrication work (give %)** | 0% (Software Project) |
| **Experimental work (give %)** | 75% (Cross-Encoder NLI entailment fact-checker implemented, factual support vs contradiction scoring verified on CUDA GPU, integrated with streaming entropy triggers) |
| **Result and Analysis** | Verified NLI entailment scoring on hallucinated claims vs reference premise; confirmed contradiction detection on factual drift with sub-35ms inference latency. |
| **Report writing** | WPR Week 7 drafted. |
| **Signature of students** | 1. Shourya Solanki &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 2. Rachit Ryan Chug &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 3. Dhruv Raj Singh |

Work done in this week (Week 7):
1. Windowed Cross-Encoder NLI Entailment Implementation: Built `src/nli_verifier.py` utilizing a Cross-Encoder architecture to classify premise-hypothesis relationships into Entailment (Factual), Neutral, or Contradiction (Hallucination).
2. Entropy-Triggered Grounding Loop: Integrated the NLI verifier with the streaming entropy engine, triggering asynchronous factual verification only when token uncertainty spikes past threshold (eliminating continuous compute overhead).
3. Latency & Contradiction Verification: Verified sub-35ms NLI cross-attention processing on local NVIDIA GeForce RTX 3050 CUDA GPU across test fact-checking cases.
4. End-to-End Dual-Stage Pipeline Integration: Connected Pre-Scan input filtration (DeBERTa-v3) with Post-Scan streaming entropy inspection and NLI verification into unified pipeline.

To be filled by Guide (strike off whichever is not applicable)
- Performance of students is satisfactory
- Performance of students is unsatisfactory
- A warning to be issued to student(s) (Name): ____________________
- Student was not well (Name): ____________________

Date: ____________________                                                              Signature of Guide: ____________________
