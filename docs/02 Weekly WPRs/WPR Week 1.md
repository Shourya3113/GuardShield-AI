Format WPR

AMITY SCHOOL OF ENGINEERING & TECHNOLOGY
B.Tech (CSE - AIML) VII Semester

Project Area -- Generative AI & AI Safety (Trustworthy AI / MLOps)

Students Weekly Progress Report (WPR) For Odd Semester of session 2026-2027

To be filled by Students:

| Field | Details |
| :--- | :--- |
| **Students Name** | 1. Shourya Solanki<br>2. Rachit Ryan Chug<br>3. Dhruv Raj Singh |
| **Roll no.** | 1. 01<br>2. 02<br>3. 03 |
| **Enrollment no.** | 1. A2305223569<br>2. A2305223166<br>3. A2305223191 |
| **Project Title finalized, if Yes, give name, if NO, give reason** | Yes. Title: "GuardShield AI: Real-Time Sidecar Proxy for LLM Hallucination Detection & Prompt Injection Defense" |
| **Synopsis submitted** | Yes (Submitted for Group No. 50) |
| **Literature review** | Completed review of 6 benchmark papers (SelfCheckGPT, JailbreakBench, Llama Guard, HaluEval, CAPTURE, TruthfulQA). Identified sub-25ms latency gap in LLM streaming guardrails. |
| **Technical & Economical Feasibility** | Feasible. Uses PyTorch, DeBERTa-v3, Ollama (Llama-3.1-8B), and FastAPI async proxy. Zero monetary cost (runs locally on developer hardware). |
| **Bill of Material** | ₹0.00 (Fully open-source software stack and local developer environment) |
| **Project Progress Schedule (PERT Chart)** | • W1-W3: Literature survey & setup (In Progress)<br>• W4-W7: Dataset concatenation & GuardShield-Bench-v1<br>• W8-W12: DeBERTa-v3 fine-tuning & token entropy algorithm<br>• W13-W16: Benchmarking & IEEE research paper<br>• W17-W30 (Sem 8): FastAPI proxy, Red-Agent & Streamlit dashboard |
| **Design of critical components** | 1. Pre-Scan DeBERTa prompt injection classifier<br>2. Post-Scan streaming token logit entropy NLI filter<br>3. FastAPI SSE sidecar proxy |
| **Fabrication work (give %)** | 0% (Software Project) |
| **Experimental work (give %)** | 15% (Local Ollama LLM setup and logit entropy testing) |
| **Result and Analysis** | Sub-25ms DeBERTa inference latency verified on local Apple Silicon MPS & CUDA GPUs. |
| **Report writing** | Synopsis submitted. WPR Week 1 completed. |
| **Signature of students** | 1. Shourya Solanki &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 2. Rachit Ryan Chug &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 3. Dhruv Raj Singh |

Work done in this week:
1. Development Environment Setup: Installed Python 3.11, PyTorch (MPS/CUDA), Ollama (Llama-3.1-8B), and FastAPI.
2. Title & Domain Finalization: Finalized "GuardShield AI" in Generative AI & AI Safety.
3. Literature Review: Reviewed 6 benchmark papers and identified the sub-25ms streaming latency research gap.
4. Architecture & PERT Schedule: Formulated dual-stage sidecar proxy architecture and 30-week milestone schedule.
5. Synopsis Submission: Formally prepared and submitted Project Synopsis for Group 50.

To be filled by Guide (strike off whichever is not applicable)
- Performance of students is satisfactory
- Performance of students is unsatisfactory
- A warning to be issued to student(s) (Name): ____________________
- Student was not well (Name): ____________________

Date: ____________________                                                              Signature of Guide: ____________________