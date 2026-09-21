Format WPR

AMITY SCHOOL OF ENGINEERING & TECHNOLOGY
B.Tech (CSE - AIML) VII Semester

Project Area -- Generative AI & AI Safety (Trustworthy AI / MLOps)

Students Weekly Progress Report (WPR — Week 8) For Odd Semester of session 2026-2027

To be filled by Students:

| Field | Details |
| :--- | :--- |
| **Students Name** | 1. Shourya Solanki<br>2. Rachit Ryan Chug<br>3. Dhruv Raj Singh |
| **Roll no.** | 1. 01<br>2. 02<br>3. 03 |
| **Enrollment no.** | 1. A2305223569<br>2. A2305223166<br>3. A2305223191 |
| **Project Title finalized, if Yes, give name, if NO, give reason** | Yes. Title: "GuardShield AI: Real-Time Sidecar Proxy for LLM Hallucination Detection & Prompt Injection Defense" |
| **Synopsis submitted** | Yes (Approved for Group No. 50) |
| **Literature review** | Applied to comparative empirical benchmarking against baseline guardrails (Meta Llama-Guard-3 and SelfCheckGPT). Analyzed latency, throughput, and compute constraints. |
| **Technical & Economical Feasibility** | Feasible. Python 3.11+, PyTorch CUDA (RTX 3050), FastAPI async proxy, DeBERTa-v3 SLM (86M). Zero monetary cost (₹0). |
| **Bill of Material** | ₹0.00 (Fully open-source software stack and local developer environment) |
| **Project Progress Schedule (PERT Chart)** | • W1-W5: Setup, dataset curation, DeBERTa fine-tuning & evaluation (Completed)<br>• W6-W8: Streaming entropy engine, NLI grounding & comparative benchmarking (Completed / Week 8)<br>• W9-W12: Multi-turn stress testing, IEEE research paper compilation & final project viva preparation |
| **Design of critical components** | 1. Comparative Benchmarking Engine (`benchmark_comparative.py`)<br>2. Baseline Comparison Matrix against Meta Llama-Guard-3 & SelfCheckGPT<br>3. Latency, VRAM footprint, and cost-per-query comparative evaluation table |
| **Fabrication work (give %)** | 0% (Software Project) |
| **Experimental work (give %)** | 85% (Comparative empirical evaluation completed; established 98% latency reduction over 8B guardrails while retaining 86.96% precision on adversarial injections) |
| **Result and Analysis** | Demonstrated GuardShield proxy achieving ~29-48ms latency overhead compared to 1650ms for Llama-Guard-3 and 3400ms for SelfCheckGPT; VRAM utilization reduced from 16GB to <500MB. |
| **Report writing** | WPR Week 8 drafted. |
| **Signature of students** | 1. Shourya Solanki &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 2. Rachit Ryan Chug &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 3. Dhruv Raj Singh |

Work done in this week (Week 8):
1. Comparative Guardrail Benchmarking: Developed `src/benchmark_comparative.py` to empirically benchmark GuardShield AI against leading industry baselines (Meta Llama-Guard-3, SelfCheckGPT, and Dense Continuous Cross-Encoders).
2. Latency & Resource Profiling: Validated that GuardShield achieves a 98.2% latency reduction over 8B guardrails (48ms vs. 1,650ms) while fitting within < 500 MB VRAM (compatible with edge/laptop hardware at ₹0 cost).
3. Streaming Support Advantage: Demonstrated that token-level Shannon entropy enables early mid-sentence hallucination termination, overcoming the 3,400ms multi-sample sampling penalty of offline detectors like SelfCheckGPT.
4. Milestone Verification: Successfully consolidated all experimental results into `data/processed/comparative_benchmark_results.json` in preparation for the IEEE research paper methodology and results sections.

To be filled by Guide (strike off whichever is not applicable)
- Performance of students is satisfactory
- Performance of students is unsatisfactory
- A warning to be issued to student(s) (Name): ____________________
- Student was not well (Name): ____________________

Date: ____________________                                                              Signature of Guide: ____________________
