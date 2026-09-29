import os
import sys
import shutil
import docx
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def build_wpr10():
    print("=" * 75)
    print("  [GuardShield AI] Generating Official WPR Week 10 (DOCX, PDF, Markdown)")
    print("=" * 75)
    base_dir = Path(__file__).resolve().parent.parent
    template_path = Path.home() / "Downloads" / "Format WPR Minor Project.docx"
    
    out_docx_docs = base_dir / "docs" / "02 Weekly WPRs" / "WPR Week 10.docx"
    out_docx_downloads = Path.home() / "Downloads" / "GuardShield_AI_WPR_Week_10.docx"
    
    out_pdf_docs = base_dir / "docs" / "02 Weekly WPRs" / "WPR Week 10.pdf"
    out_pdf_downloads = Path.home() / "Downloads" / "GuardShield_AI_WPR_Week_10.pdf"
    
    out_md_docs = base_dir / "docs" / "02 Weekly WPRs" / "WPR Week 10.md"
    
    doc = docx.Document(template_path)
    
    # 1. Update Header Paragraphs
    doc.paragraphs[2].text = 'AMITY SCHOOL OF ENGINEERING & TECHNOLOGY'
    doc.paragraphs[3].text = 'B.Tech (CSE - AIML)  VII Semester'
    doc.paragraphs[6].text = 'Project Area -- Generative AI & AI Safety (Trustworthy AI / MLOps)'
    doc.paragraphs[9].text = 'Students Weekly Progress Report (WPR — Week 10) For Odd Semester of session 2026-2027'
    
    # 2. Fill Table 0 (Academic Metadata)
    t0 = doc.tables[0]
    
    t0.rows[0].cells[1].text = 'Group No. 50'
    t0.rows[1].cells[1].text = '1. Shourya Solanki\n2. Rachit Ryan Chug\n3. Dhruv Raj Singh'
    t0.rows[2].cells[1].text = '1. 01\n2. 02\n3. 03'
    t0.rows[3].cells[1].text = '1. A2305223569\n2. A2305223166\n3. A2305223191'
    t0.rows[4].cells[1].text = 'Yes. Title: "GuardShield AI: Real-Time Sidecar Proxy for LLM Hallucination Detection & Prompt Injection Defense"'
    t0.rows[5].cells[1].text = 'Yes (Approved for Group No. 50)'
    t0.rows[6].cells[1].text = 'Integrated published peer-reviewed benchmark datasets: Stanford SPML Chatbot Injections (16K), Jayavibhav Benchmark (327K), Deepset Benchmark, ChatGPT JailbreakBench DAN Personas, FEVER Gold Evidence (NAACL 2018), and HaluEval QA Benchmark (EMNLP 2023). Conducted formal literature survey on NLI formulation, length bias confounders, and streaming token uncertainty metrics.'
    t0.rows[7].cells[1].text = 'Feasible. Evaluated on local NVIDIA GeForce RTX 3050 GPU (4GB VRAM), PyTorch 2.6 CUDA, Hugging Face Transformers, DeBERTa-v3 SLM (44.3M backbone, 142.6M total params). Zero monetary expenditure (₹0).'
    t0.rows[8].cells[1].text = '₹0.00 (Fully open-source software stack, public academic benchmark datasets, and local developer environment)'
    t0.rows[9].cells[1].text = '• W1-W5: Problem formulation, dataset curation, DeBERTa fine-tuning & evaluation (Completed)\n• W6-W8: Streaming entropy engine, NLI fact verifier, and multi-model benchmarking (Completed)\n• W9: Mega benchmark scaling across 5,948 samples, stratified splits, and in-dist/OOD validation (Completed)\n• W10: Stage 2 authentic benchmark integration (FEVER + HaluEval), NLI declarative statement formulation, 95% Wilson confidence intervals, length-matched scientific controls, real empirical E2E sequential latency measurement, and entropy engine threshold recalibration (Completed / Week 10)\n• W11-W12: IEEE/ACM conference research paper manuscript drafting, ablation study documentation, and final viva defense preparation.'
    t0.rows[10].cells[1].text = '1. Authentic Multi-Source Fact Grounding Extractor (`scripts/build_authentic_stage2_data.py`)\n2. Scientific Rigor & Statistical Controls Pipeline (`scripts/evaluate_statistical_rigor.py`)\n3. Empirical Sequential End-to-End Latency Measurement Suite (`scripts/measure_pipeline_e2e_latency.py`)\n4. Normalized Top-k Streaming Token Entropy Engine with Concurrency Isolation (`src/streaming_entropy_engine.py`)\n5. Model Weights Checkpoint Manager & Verification Utility (`scripts/download_weights.py`)'
    t0.rows[11].cells[1].text = '0% (Software Project)'
    t0.rows[12].cells[1].text = '95% (Stage 1 & Stage 2 empirical evaluations complete; statistical significance, Wilson CIs, length controls, and raw prediction logs verified)'
    t0.rows[13].cells[1].text = 'Stage 1 achieves 98.42% ± 0.96% in-distribution test accuracy (97.75% recall, 0.87% FPR, 32.95ms p50) and 98.20% ± 1.22% zero-shot OOD accuracy (85.53%–92.11% on authentic human DAN jailbreaks, 100% on templated shifts, 18.48ms p50). Length-matched controls prove 98.48% accuracy vs 60.61% for length heuristics. Stage 2 declarative grounding achieves 73.25% ± 3.06% accuracy (86.50% on FEVER, 60.00% on HaluEval, 18.91ms p50). Measured sequential E2E pipeline overhead is 65.86ms p50 / 68.47ms mean across 100 real CUDA queries.'
    t0.rows[14].cells[1].text = 'WPR Week 10 drafted, verified with raw prediction logs, and formatted.'
    t0.rows[15].cells[1].text = '1. Shourya Solanki         2. Rachit Ryan Chug         3. Dhruv Raj Singh'
    
    # 3. Fill Work Done Paragraph
    p11 = doc.paragraphs[11]
    work_done_text = (
        'Work done in this week (Week 10):\n'
        '1. Authentic Academic Fact Grounding Ingestion (FEVER NAACL + HaluEval EMNLP): Ingested 100% genuine, non-duplicated benchmark pairs directly from published literature: 400 claim-evidence pairs from FEVER (copenlu/fever_gold_evidence, NAACL 2018) and 400 question-answering pairs from HaluEval (pminervini/HaluEval, EMNLP 2023), eliminating all synthetic prefixes and artificial loops.\n'
        '2. Declarative Hypothesis Formulation for NLI Verification: Resolved length and syntactic confounding where extractive answers were bare entities (12.5 chars) while hallucinations were full sentences (58 chars). Re-formulated QA pairs into complete declarative statements ("The answer to the question \'{question}\' is {answer}."). Achieved 86.50% accuracy and 88.50% recall on FEVER, and 60.00% accuracy on HaluEval (73.25% overall, 76.88% precision, 66.50% recall, 20.00% FPR).\n'
        '3. Empirical Sequential End-to-End Pipeline Latency: Conducted 100 real sequential queries measuring the combined defense overhead (Stage 1 with sliding-window chunking followed by Stage 2 NLI fact verification) with hardware CUDA synchronization on local NVIDIA GPU. Established an empirical median (p50) latency of 65.86 ms, mean of 68.47 ms (±11.58 ms), and p95 of 84.43 ms, logged per-sample in `raw_eval_pipeline_e2e.json`.\n'
        '4. Statistical Rigor, Confidence Intervals & Scientific Controls: Implemented 95% Wilson score binomial confidence intervals across all benchmarks: Stage 1 In-Dist (98.42% ± 0.96%), Zero-Shot OOD (98.20% ± 1.22%), Stage 2 Fact Grounding (73.25% ± 3.06%). Conducted a balanced length-matched control experiment (100–350 chars), proving GuardShield maintains 98.48% accuracy while a length heuristic collapses to 60.61%. Audited 66 long safe prompts (>= 200 chars), verifying low sliding-window FPR (4.55%, 36.65 ms p50).\n'
        '5. Mathematical Refinement of Streaming Token Entropy: Refactored the streaming entropy engine to compute normalized top-k conditional Shannon entropy bounded in [0, log2(k)], calibrated threshold to 1.25 bits, and verified that realistic generation distributions ([0.6, 0.2, 0.1] -> 1.22 bits) do not cause false alarms, while flat uncertainty ([0.34, 0.33, 0.33] -> 1.58 bits) triggers early termination. Implemented per-session isolation in the proxy to eliminate concurrency state corruption.\n'
        '6. Transparent OOD Breakdown & Reviewer Verifiability: Disclosed the nuanced OOD breakdown (85.53%–92.11% recall on authentic human DAN jailbreaks vs 100% on templated shifts), exported complete per-sample prediction logs (`raw_eval_*.json`) for hardware-independent reviewer validation, and upgraded `scripts/download_weights.py` with automated local fine-tuning and Hugging Face Hub download support.'
    )
    p11.text = work_done_text
    
    # 4. Save DOCX Files
    doc.save(out_docx_docs)
    if out_docx_downloads.parent.exists():
        doc.save(out_docx_downloads)
    print(f"✅ Saved WPR 10 DOCX at:\n   - {out_docx_docs}\n   - {out_docx_downloads}")
    
    # 5. Write Markdown Version
    md_content = f"""Format WPR

AMITY SCHOOL OF ENGINEERING & TECHNOLOGY
B.Tech (CSE - AIML) VII Semester

Project Area -- Generative AI & AI Safety (Trustworthy AI / MLOps)

Students Weekly Progress Report (WPR — Week 10) For Odd Semester of session 2026-2027

To be filled by Students:

| Field | Details |
| :--- | :--- |
| **Students Name** | 1. Shourya Solanki<br>2. Rachit Ryan Chug<br>3. Dhruv Raj Singh |
| **Roll no.** | 1. 01<br>2. 02<br>3. 03 |
| **Enrollment no.** | 1. A2305223569<br>2. A2305223166<br>3. A2305223191 |
| **Project Title finalized, if Yes, give name, if NO, give reason** | Yes. Title: "GuardShield AI: Real-Time Sidecar Proxy for LLM Hallucination Detection & Prompt Injection Defense" |
| **Synopsis submitted** | Yes (Approved for Group No. 50) |
| **Literature review** | Integrated published peer-reviewed benchmark datasets: Stanford SPML Chatbot Injections (16K), Jayavibhav Benchmark (327K), Deepset Benchmark, ChatGPT JailbreakBench DAN Personas, FEVER Gold Evidence (NAACL 2018), and HaluEval QA Benchmark (EMNLP 2023). Conducted formal literature survey on NLI formulation, length bias confounders, and streaming token uncertainty metrics. |
| **Technical & Economical Feasibility** | Feasible. Evaluated on local NVIDIA GeForce RTX 3050 GPU (4GB VRAM), PyTorch 2.6 CUDA, Hugging Face Transformers, DeBERTa-v3 SLM (44.3M backbone, 142.6M total params). Zero monetary expenditure (₹0). |
| **Bill of Material** | ₹0.00 (Fully open-source software stack, public academic benchmark datasets, and local developer environment) |
| **Project Progress Schedule (PERT Chart)** | • W1-W5: Problem formulation, dataset curation, DeBERTa fine-tuning & evaluation (Completed)<br>• W6-W8: Streaming entropy engine, NLI fact verifier, and multi-model benchmarking (Completed)<br>• W9: Mega benchmark scaling across 5,948 samples, stratified splits, and in-dist/OOD validation (Completed)<br>• W10: Stage 2 authentic benchmark integration (FEVER + HaluEval), NLI declarative statement formulation, 95% Wilson confidence intervals, length-matched scientific controls, real empirical E2E sequential latency measurement, and entropy engine threshold recalibration (Completed / Week 10)<br>• W11-W12: IEEE/ACM conference research paper manuscript drafting, ablation study documentation, and final viva defense preparation. |
| **Design of critical components** | 1. Authentic Multi-Source Fact Grounding Extractor (`scripts/build_authentic_stage2_data.py`)<br>2. Scientific Rigor & Statistical Controls Pipeline (`scripts/evaluate_statistical_rigor.py`)<br>3. Empirical Sequential End-to-End Latency Measurement Suite (`scripts/measure_pipeline_e2e_latency.py`)<br>4. Normalized Top-k Streaming Token Entropy Engine with Concurrency Isolation (`src/streaming_entropy_engine.py`)<br>5. Model Weights Checkpoint Manager & Verification Utility (`scripts/download_weights.py`) |
| **Fabrication work (give %)** | 0% (Software Project) |
| **Experimental work (give %)** | 95% (Stage 1 & Stage 2 empirical evaluations complete; statistical significance, Wilson CIs, length controls, and raw prediction logs verified) |
| **Result and Analysis** | Stage 1 achieves 98.42% ± 0.96% in-distribution test accuracy (97.75% recall, 0.87% FPR, 32.95ms p50) and 98.20% ± 1.22% zero-shot OOD accuracy (85.53%–92.11% on authentic human DAN jailbreaks, 100% on templated shifts, 18.48ms p50). Length-matched controls prove 98.48% accuracy vs 60.61% for length heuristics. Stage 2 declarative grounding achieves 73.25% ± 3.06% accuracy (86.50% on FEVER, 60.00% on HaluEval, 18.91ms p50). Measured sequential E2E pipeline overhead is 65.86ms p50 / 68.47ms mean across 100 real CUDA queries. |
| **Report writing** | WPR Week 10 drafted, verified with raw prediction logs, and formatted. |
| **Signature of students** | 1. Shourya Solanki &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 2. Rachit Ryan Chug &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 3. Dhruv Raj Singh |

{work_done_text}

To be filled by Guide (strike off whichever is not applicable)
- Performance of students is satisfactory
- Performance of students is unsatisfactory
- A warning to be issued to student(s) (Name): ____________________
- Student was not well (Name): ____________________

Date: ____________________                                                              Signature of Guide: ____________________
"""
    with open(out_md_docs, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"✅ Saved WPR 10 Markdown at:\n   - {out_md_docs}")
    
    # 6. Convert to PDF using MS Word COM Automation
    try:
        import win32com.client
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        
        doc_in = word.Documents.Open(os.path.abspath(out_docx_docs))
        doc_in.SaveAs(os.path.abspath(out_pdf_docs), FileFormat=17) # 17 = wdFormatPDF
        doc_in.Close()
        
        if out_pdf_downloads.parent.exists():
            shutil.copy(out_pdf_docs, out_pdf_downloads)
        word.Quit()
        print(f"✅ Successfully converted and saved WPR 10 PDF at:\n   - {out_pdf_docs}\n   - {out_pdf_downloads}")
    except Exception as e:
        print(f"⚠️ PDF Conversion note: {e}")

if __name__ == "__main__":
    build_wpr10()
