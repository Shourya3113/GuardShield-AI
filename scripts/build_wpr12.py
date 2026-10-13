import os
import sys
import shutil
import docx
from pathlib import Path

if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

def build_wpr12():
    print("=" * 75)
    print("  [GuardShield AI] Generating Official WPR Week 12 (DOCX, PDF, Markdown)")
    print("=" * 75)
    base_dir = Path(__file__).resolve().parent.parent
    template_path = Path.home() / "Downloads" / "Format WPR Minor Project.docx"
    
    out_docx_docs = base_dir / "docs" / "02 Weekly WPRs" / "WPR Week 12.docx"
    out_docx_downloads = Path.home() / "Downloads" / "GuardShield_AI_WPR_Week_12.docx"
    
    out_pdf_docs = base_dir / "docs" / "02 Weekly WPRs" / "WPR Week 12.pdf"
    out_pdf_downloads = Path.home() / "Downloads" / "GuardShield_AI_WPR_Week_12.pdf"
    
    out_md_docs = base_dir / "docs" / "02 Weekly WPRs" / "WPR Week 12.md"
    
    doc = docx.Document(template_path)
    
    # 1. Update Header Paragraphs
    doc.paragraphs[2].text = 'AMITY SCHOOL OF ENGINEERING & TECHNOLOGY'
    doc.paragraphs[3].text = 'B.Tech (CSE - AIML)  VII Semester'
    doc.paragraphs[6].text = 'Project Area -- Generative AI & AI Safety (Trustworthy AI / MLOps)'
    doc.paragraphs[9].text = 'Students Weekly Progress Report (WPR — Week 12) For Odd Semester of session 2026-2027'
    
    # 2. Fill Table 0 (Academic Metadata)
    t0 = doc.tables[0]
    
    t0.rows[0].cells[1].text = 'Group No. 50'
    t0.rows[1].cells[1].text = '1. Shourya Solanki\n2. Rachit Ryan Chug\n3. Dhruv Raj Singh'
    t0.rows[2].cells[1].text = '1. 01\n2. 02\n3. 03'
    t0.rows[3].cells[1].text = '1. A2305223569\n2. A2305223166\n3. A2305223191'
    t0.rows[4].cells[1].text = 'Yes. Title: "GuardShield AI: Real-Time Sidecar Proxy for LLM Hallucination Detection & Prompt Injection Defense"'
    t0.rows[5].cells[1].text = 'Yes (Approved for Group No. 50)'
    t0.rows[6].cells[1].text = (
        'Synthesized contemporary AI safety and prompt injection guard literature (September–October 2026 preprints): '
        'Liu et al. on benchmark contamination (arXiv:2610.03448), Zhang et al. on paired benign-twin controls (arXiv:2609.26176), '
        'HiveTraceGuard-Pro on recall/FPR trade-offs (arXiv:2609.01046), and PIDS-Bench. Formulated the Paired Joint Accuracy (PJA) '
        'evaluation metric and executed an exhaustive paired audit across 17 open-weight and commercial prompt-injection detectors '
        'and safety SLMs, demonstrating format-triggered over-defense and tokenizer fragmentation bias.'
    )
    t0.rows[7].cells[1].text = (
        'Feasible. Dual-tier evaluation framework executed across local NVIDIA RTX 3050 GPU (4GB VRAM) for low-latency inference '
        '(<30ms Stage 1, <31ms Stage 2) and cloud-accelerated Kaggle/Colab environments (NVIDIA T4, L4, A100 GPUs) for multi-model '
        'parallel evaluation (17 models, 12,000+ evaluated pairs). Open-source software stack with zero licensing expenditure (₹0).'
    )
    t0.rows[8].cells[1].text = '₹0.00 (Fully open-source software stack, public academic benchmark datasets, Hugging Face Hub open-weight models, and local developer environment)'
    t0.rows[9].cells[1].text = (
        '• W1-W5: Problem formulation, dataset curation, DeBERTa fine-tuning & evaluation (Completed)\n'
        '• W6-W8: Streaming entropy engine, NLI fact verifier, and multi-model benchmarking (Completed)\n'
        '• W9-W10: Stage 2 authentic benchmark integration (FEVER + HaluEval), NLI declarative statements, 95% Wilson CIs, and E2E latency measurement (Completed)\n'
        '• W11: Interactive unified pipeline with multi-model backbone switching, negative refutation hallucination resolution, 15k massive multi-domain dataset curation, and high-VRAM DeBERTa-v3-large trainer (Completed)\n'
        '• W12: Comprehensive 17-guard paired perturbation audit (Study A: 12 families, 500 pairs), native Hindi/Hinglish benchmark curation (Study B: 400 seeds), pre-registered research spec (SPEC.md), novelty gap analysis against 2026 preprints, and Paper 1 manuscript preparation for IEEE/ACM submission (Completed / Week 12)'
    )
    t0.rows[10].cells[1].text = (
        '1. Paired-Perturbation Audit Harness & PJA Metric Engine (guard_audit/perturbations.py & paper1/SPEC.md)\n'
        '2. Native Multilingual & Hinglish Diagnostic Benchmark Suite (paper1/annotation/seeds.csv & validate_seeds.py)\n'
        '3. Multi-Guard Evaluation Engine for 17 SOTA Defenses (paper1/runs/obf_main/ across Llama-Guard-3, Prompt-Guard-2, ProtectAI, Qwen3Guard, Sentinel-v2, WildGuard)\n'
        '4. Cryptographic HMAC-SHA256 Signed Assistant History Proxy (src/proxy_server.py)\n'
        '5. Automated LaTeX Table & Manuscript Compilation Pipeline (scripts/generate_readme_tables.py & paper1/runs/obf_main/)'
    )
    t0.rows[11].cells[1].text = '0% (Software Project)'
    t0.rows[12].cells[1].text = '100% (Stage 1, Stage 2, and 17-Guard comparative audit completed; 12 paired perturbation families evaluated; 500 pairs scored per guard; multi-turn signed history verified with 0% false block rate)'
    t0.rows[13].cells[1].text = (
        'Demonstrated that attack-only evaluations are fundamentally misleading: under character obfuscation (zero-width, soft-hyphen, leetspeak, homoglyphs), '
        'small classifiers (Deepset, FMOps, Mezzo) suffer blanket fail-closed collapse (FPR rises to 79.4%–100.0% on benign twins), masquerading as high attack recall. '
        'Horizon Guard Base and Qwen3Guard-8B maintained superior Paired Joint Accuracy (PJA 93.8%–98.8%). GuardShield Stage 1 with HMAC assistant signing achieved '
        '0.00% conversation block rate on multi-turn dialogue (vs 20.00% for ProtectAI) and 3.08% FPR on hard benigns with 60.52 ms median E2E latency.'
    )
    t0.rows[14].cells[1].text = 'WPR Week 12 drafted, verified with authoritative empirical audit logs across 17 guards, and formatted.'
    t0.rows[15].cells[1].text = '1. Shourya Solanki         2. Rachit Ryan Chug         3. Dhruv Raj Singh'
    
    # 3. Fill Work Done Paragraph
    p11 = doc.paragraphs[11]
    work_done_text = (
        'Work done in this week (Week 12):\n'
        '1. Paper 1 Formal Formulation, Hypotheses Pre-Registration & Landscape Review: Formulated and registered the formal experimental specification (`paper1/SPEC.md`) titled "Guards that reject the unfamiliar: format-triggered over-defense in prompt-injection detectors". Conducted exhaustive novelty verification (`reports/Guardrail paper novelty check.md` and `reports/LLM guardrail research gaps.md`) against late-2026 preprints (Liu arXiv:2610.03448, Zhang arXiv:2609.26176, HiveTraceGuard arXiv:2609.01046, PIDS-Bench). Pre-registered core hypotheses (H1–H5), establishing the Paired Joint Accuracy (PJA) evaluation metric where both an attack and its length-matched benign twin must be classified correctly under identical, label-blind transformations.\n'
        '2. Large-Scale Paired Obfuscation Audit Across 17 SOTA Prompt Injection Guards (Study A): Engineered and executed a comprehensive multi-model audit harness evaluating 17 guardrails and safety SLMs: GuardShield DeBERTa-v3, ProtectAI v2, Meta Prompt Guard 1 (classifier + jailbreak), Meta Prompt Guard 2 (22M & 86M), Meta Llama Guard 3 (1B & 8B), Deepset, FMOps, Horizon Guard Base, Mezzo v2 Base, Perplexity GPT-2, Qwen3Guard (0.6B & 8B), Sentinel v2, and WildGuard. Tested 500 attack-benign pairs (1,000 prompts per condition) across 12 perturbation families: `clean`, `zero_width`, `soft_hyphen`, `leetspeak`, `homoglyph`, `base64_wrap`, `base64_scaffold`, `rot13_wrap`, `rot13_scaffold`, `fullwidth`, `diacritics`, and `spaced_letters`.\n'
        '3. Empirical Discovery of Format Over-Defense, Fail-Closed Bias & Scaffold Controls: Uncovered that traditional attack-only recall benchmarks are severely confounded: under zero-width spaces, soft-hyphens, and homoglyphs, baseline classifiers (Deepset, FMOps, Mezzo) exhibit near 100% attack recall only because their benign twin FPR surges to 79.4%–100.0% (blanket fail-closed rejection). Introduced label-blind scaffold controls (`base64_scaffold`, `rot13_scaffold`) with identical plain-text phrasing, proving that wrapper rejections are driven primarily by prompt template phrasing rather than base64 decoding ability. Tracked token-length truncation profiles across all guards to prevent unfair evaluation.\n'
        '4. Native Multilingual & Hinglish Diagnostic Benchmark Curation (Study B): Designed and curated a 400-seed diagnostic evaluation benchmark (`paper1/annotation/seeds.csv`) covering English (`en`), Devanagari Hindi (`hi_deva`), Romanized Hindi (`hi_roman`), and Hindi-English code-mixing (`hinglish`) across 5 critical injection categories and benign everyday tasks (30% trigger-word split). Authored strict annotation guidelines (`paper1/annotation/GUIDELINES.md`) mandating native-speaker composition (excluding machine translation artifacts) and developed an automated seed validation tool (`paper1/annotation/validate_seeds.py`) enforcing register consistency and Cohen\'s κ label checks.\n'
        '5. Cloud-Scale Kaggle / Colab Automated Benchmarking Architecture: Developed turnkey Kaggle and Google Colab execution environments (`paper1/NOTEBOOK_SETUP.md`) supporting single-pass verdict scoring across NVIDIA T4, L4, A100, and TPU v5e accelerators. Implemented exponential backoff retry mechanisms for Hugging Face Hub API rate limits, dynamic chunk-size adaptations for generative guards (Llama Guard 3, Qwen3Guard, WildGuard), and automated JSON/JSONL score serialization with SHA-256 dataset manifests.\n'
        '6. Rigorous Audit Remediation, HMAC Assistant Signing & Production Hardening: Resolved all independent technical auditor findings (Re-Audit #6 and #7). Deployed cryptographic HMAC-SHA256 assistant response signing in `src/proxy_server.py`, ensuring authentic multi-turn LLM replies are recognized without scanning while keeping user inputs and forged assistant turns under unconditional neural inspection. Achieved 0.00% conversation false blocks on multi-turn dialogue (vs. 20.00% for ProtectAI) and reduced benign-hard FPR to 3.08%, with clean git commit synchronization and verified packaging under 500 MB.'
    )
    p11.text = work_done_text
    
    # 4. Save DOCX Files
    doc.save(out_docx_docs)
    if out_docx_downloads.parent.exists():
        doc.save(out_docx_downloads)
    print(f"✅ Saved WPR 12 DOCX at:\n   - {out_docx_docs}\n   - {out_docx_downloads}")
    
    # 5. Write Markdown Version
    md_content = f"""Format WPR

AMITY SCHOOL OF ENGINEERING & TECHNOLOGY
B.Tech (CSE - AIML) VII Semester

Project Area -- Generative AI & AI Safety (Trustworthy AI / MLOps)

Students Weekly Progress Report (WPR — Week 12) For Odd Semester of session 2026-2027

To be filled by Students:

| Field | Details |
| :--- | :--- |
| **Students Name** | 1. Shourya Solanki<br>2. Rachit Ryan Chug<br>3. Dhruv Raj Singh |
| **Roll no.** | 1. 01<br>2. 02<br>3. 03 |
| **Enrollment no.** | 1. A2305223569<br>2. A2305223166<br>3. A2305223191 |
| **Project Title finalized, if Yes, give name, if NO, give reason** | Yes. Title: "GuardShield AI: Real-Time Sidecar Proxy for LLM Hallucination Detection & Prompt Injection Defense" |
| **Synopsis submitted** | Yes (Approved for Group No. 50) |
| **Literature review** | Synthesized contemporary AI safety and prompt injection guard literature (September–October 2026 preprints): Liu et al. on benchmark contamination (arXiv:2610.03448), Zhang et al. on paired benign-twin controls (arXiv:2609.26176), HiveTraceGuard-Pro on recall/FPR trade-offs (arXiv:2609.01046), and PIDS-Bench. Formulated the Paired Joint Accuracy (PJA) evaluation metric and executed an exhaustive paired audit across 17 open-weight and commercial prompt-injection detectors and safety SLMs, demonstrating format-triggered over-defense and tokenizer fragmentation bias. |
| **Technical & Economical Feasibility** | Feasible. Dual-tier evaluation framework executed across local NVIDIA RTX 3050 GPU (4GB VRAM) for low-latency inference (<30ms Stage 1, <31ms Stage 2) and cloud-accelerated Kaggle/Colab environments (NVIDIA T4, L4, A100 GPUs) for multi-model parallel evaluation (17 models, 12,000+ evaluated pairs). Open-source software stack with zero licensing expenditure (₹0). |
| **Bill of Material** | ₹0.00 (Fully open-source software stack, public academic benchmark datasets, Hugging Face Hub open-weight models, and local developer environment) |
| **Project Progress Schedule (PERT Chart)** | • W1-W5: Problem formulation, dataset curation, DeBERTa fine-tuning & evaluation (Completed)<br>• W6-W8: Streaming entropy engine, NLI fact verifier, and multi-model benchmarking (Completed)<br>• W9-W10: Stage 2 authentic benchmark integration (FEVER + HaluEval), NLI declarative statements, 95% Wilson CIs, and E2E latency measurement (Completed)<br>• W11: Interactive unified pipeline with multi-model backbone switching, negative refutation hallucination resolution, 15k massive multi-domain dataset curation, and high-VRAM DeBERTa-v3-large trainer (Completed)<br>• W12: Comprehensive 17-guard paired perturbation audit (Study A: 12 families, 500 pairs), native Hindi/Hinglish benchmark curation (Study B: 400 seeds), pre-registered research spec (SPEC.md), novelty gap analysis against 2026 preprints, and Paper 1 manuscript preparation for IEEE/ACM submission (Completed / Week 12) |
| **Design of critical components** | 1. Paired-Perturbation Audit Harness & PJA Metric Engine (`guard_audit/perturbations.py` & `paper1/SPEC.md`)<br>2. Native Multilingual & Hinglish Diagnostic Benchmark Suite (`paper1/annotation/seeds.csv` & `validate_seeds.py`)<br>3. Multi-Guard Evaluation Engine for 17 SOTA Defenses (`paper1/runs/obf_main/` across Llama-Guard-3, Prompt-Guard-2, ProtectAI, Qwen3Guard, Sentinel-v2, WildGuard)<br>4. Cryptographic HMAC-SHA256 Signed Assistant History Proxy (`src/proxy_server.py`)<br>5. Automated LaTeX Table & Manuscript Compilation Pipeline (`scripts/generate_readme_tables.py` & `paper1/runs/obf_main/`) |
| **Fabrication work (give %)** | 0% (Software Project) |
| **Experimental work (give %)** | 100% (Stage 1, Stage 2, and 17-Guard comparative audit completed; 12 paired perturbation families evaluated; 500 pairs scored per guard; multi-turn signed history verified with 0% false block rate) |
| **Result and Analysis** | Demonstrated that attack-only evaluations are fundamentally misleading: under character obfuscation (zero-width, soft-hyphen, leetspeak, homoglyphs), small classifiers (Deepset, FMOps, Mezzo) suffer blanket fail-closed collapse (FPR rises to 79.4%–100.0% on benign twins), masquerading as high attack recall. Horizon Guard Base and Qwen3Guard-8B maintained superior Paired Joint Accuracy (PJA 93.8%–98.8%). GuardShield Stage 1 with HMAC assistant signing achieved 0.00% conversation block rate on multi-turn dialogue (vs 20.00% for ProtectAI) and 3.08% FPR on hard benigns with 60.52 ms median E2E latency. |
| **Report writing** | WPR Week 12 drafted, verified with authoritative empirical audit logs across 17 guards, and formatted. |
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
    print(f"✅ Saved WPR 12 Markdown at:\n   - {out_md_docs}")
    
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
        print(f"✅ Successfully converted and saved WPR 12 PDF at:\n   - {out_pdf_docs}\n   - {out_pdf_downloads}")
    except Exception as e:
        print(f"⚠️ PDF Conversion note: {e}")

if __name__ == "__main__":
    build_wpr12()
