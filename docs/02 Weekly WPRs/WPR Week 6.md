Format WPR

AMITY SCHOOL OF ENGINEERING & TECHNOLOGY
B.Tech (CSE - AIML) VII Semester

Project Area -- Generative AI & AI Safety (Trustworthy AI / MLOps)

Students Weekly Progress Report (WPR — Week 6) For Odd Semester of session 2026-2027

To be filled by Students:

| Field | Details |
| :--- | :--- |
| **Students Name** | 1. Shourya Solanki<br>2. Rachit Ryan Chug<br>3. Dhruv Raj Singh |
| **Roll no.** | 1. 01<br>2. 02<br>3. 03 |
| **Enrollment no.** | 1. A2305223569<br>2. A2305223166<br>3. A2305223191 |
| **Project Title finalized, if Yes, give name, if NO, give reason** | Yes. Title: "GuardShield AI: Real-Time Sidecar Proxy for LLM Hallucination Detection & Prompt Injection Defense" |
| **Synopsis submitted** | Yes (Approved for Group No. 50) |
| **Literature review** | Applied to streaming token entropy and async sidecar proxy. Integrated Shannon entropy math with FastAPI SSE streaming. |
| **Technical & Economical Feasibility** | Feasible. Python 3.11+, PyTorch CUDA, FastAPI, Uvicorn, Streaming SSE, DeBERTa-v3 SLM (86M). Zero monetary cost (₹0). |
| **Bill of Material** | ₹0.00 (Fully open-source software stack and local developer environment) |
| **Project Progress Schedule (PERT Chart)** | • W1-W5: Setup, dataset curation, DeBERTa fine-tuning & evaluation (Completed)<br>• W6-W8: Streaming entropy engine, early termination & FastAPI sidecar proxy (In Progress / Week 6)<br>• W9-W12: NLI cross-encoder integration, comparative benchmarking & final IEEE paper |
| **Design of critical components** | 1. Streaming Token Entropy Engine (`streaming_entropy_engine.py`)<br>2. Consecutive Spike Early Termination Controller<br>3. FastAPI Async Sidecar Proxy Server Prototype (`proxy_server.py`) |
| **Fabrication work (give %)** | 0% (Software Project) |
| **Experimental work (give %)** | 65% (Real-time streaming entropy calculator implemented, early termination triggers verified on hallucinated token sequences, FastAPI proxy server prototype built) |
| **Result and Analysis** | Verified sliding-window Shannon entropy H(x) on streaming logits; confirmed early stream termination on sustained spikes (>1.20 bits), preventing delivery of hallucinated tokens. |
| **Report writing** | WPR Week 6 drafted. |
| **Signature of students** | 1. Shourya Solanki &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 2. Rachit Ryan Chug &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 3. Dhruv Raj Singh |

Work done in this week (Week 6):
1. Streaming Token Entropy Module Implementation: Built `src/streaming_entropy_engine.py` to calculate Shannon Entropy H(x) = -sum(p * log2(p)) over discrete token probability distributions in real time.
2. Consecutive Spike Early Termination Logic: Designed and verified threshold-based early termination triggering when uncertainty spikes past 1.20 bits across consecutive tokens, halting hallucinated text mid-sentence.
3. FastAPI Sidecar Proxy Server Prototype: Developed `src/proxy_server.py` with `/v1/chat/completions` endpoint featuring asynchronous Pre-Scan security interception and Server-Sent Events (SSE) streaming token output.
4. Pre-Scan + Post-Scan Integration: Linked the fine-tuned DeBERTa-v3 classifier as pre-routing security middleware, returning 403 Forbidden with risk scores on detected prompt injection attempts.

To be filled by Guide (strike off whichever is not applicable)
- Performance of students is satisfactory
- Performance of students is unsatisfactory
- A warning to be issued to student(s) (Name): ____________________
- Student was not well (Name): ____________________

Date: ____________________                                                              Signature of Guide: ____________________
