import docx

def update_wpr():
    template_path = r'C:\Users\Peter\Downloads\Format WPR Minor Project.docx'
    out_docx_path = r'd:\projects\GuardShield_AI\GuardShield_AI_WPR_Week_1.docx'
    fallback_path = r'd:\projects\GuardShield_AI\GuardShield_AI_WPR_Week_1_Brief.docx'
    
    doc = docx.Document(template_path)
    
    # Update Header Paragraphs while keeping exact template layout
    doc.paragraphs[2].text = 'AMITY SCHOOL OF ENGINEERING & TECHNOLOGY'
    doc.paragraphs[3].text = 'B.Tech (CSE - AIML)  VII Semester'
    doc.paragraphs[6].text = 'Project Area -- Generative AI & AI Safety (Trustworthy AI / MLOps)'
    doc.paragraphs[9].text = 'Students Weekly Progress Report (WPR) For Odd Semester of session 2026-2027'
    
    # Fill Table 0 Cell 1 (Row details - Brief & Concise)
    t0 = doc.tables[0]
    
    t0.rows[0].cells[1].text = 'Group No. 50'
    t0.rows[1].cells[1].text = '1. Shourya Solanki\n2. Rachit Ryan Chug\n3. Dhruv Raj Singh'
    t0.rows[2].cells[1].text = '1. 01\n2. 02\n3. 03'
    t0.rows[3].cells[1].text = '1. A2305223569\n2. A2305223166\n3. A2305223191'
    t0.rows[4].cells[1].text = 'Yes. Title: "GuardShield AI: Real-Time Sidecar Proxy for LLM Hallucination Detection & Prompt Injection Defense"'
    t0.rows[5].cells[1].text = 'Yes (Submitted for Group No. 50)'
    t0.rows[6].cells[1].text = 'Completed review of 6 benchmark papers (SelfCheckGPT, JailbreakBench, Llama Guard, HaluEval, CAPTURE, TruthfulQA). Identified sub-25ms latency gap in LLM streaming guardrails.'
    t0.rows[7].cells[1].text = 'Feasible. Uses PyTorch, DeBERTa-v3, Ollama (Llama-3.1-8B), and FastAPI async proxy. Zero monetary cost (runs locally on developer hardware).'
    t0.rows[8].cells[1].text = '₹0.00 (Fully open-source software stack and local developer environment)'
    t0.rows[9].cells[1].text = '• W1-W3: Literature survey & setup (In Progress)\n• W4-W7: Dataset concatenation & GuardShield-Bench-v1\n• W8-W12: DeBERTa-v3 fine-tuning & token entropy algorithm\n• W13-W16: Benchmarking & IEEE research paper\n• W17-W30 (Sem 8): FastAPI proxy, Red-Agent & Streamlit dashboard'
    t0.rows[10].cells[1].text = '1. Pre-Scan DeBERTa prompt injection classifier\n2. Post-Scan streaming token logit entropy NLI filter\n3. FastAPI SSE sidecar proxy'
    t0.rows[11].cells[1].text = '0% (Software Project)'
    t0.rows[12].cells[1].text = '15% (Local Ollama LLM setup and logit entropy testing)'
    t0.rows[13].cells[1].text = 'Sub-25ms DeBERTa inference latency verified on local Apple Silicon MPS & CUDA GPUs.'
    t0.rows[14].cells[1].text = 'Synopsis submitted. WPR Week 1 completed.'
    t0.rows[15].cells[1].text = '1. Shourya Solanki         2. Rachit Ryan Chug         3. Dhruv Raj Singh'
    
    # Fill Work done in this week paragraph area
    p11 = doc.paragraphs[11]
    p11.text = 'Work done in this week:\n' \
               '1. Development Environment Setup: Installed Python 3.11, PyTorch (MPS/CUDA), Ollama (Llama-3.1-8B), and FastAPI.\n' \
               '2. Title & Domain Finalization: Finalized "GuardShield AI" in Generative AI & AI Safety.\n' \
               '3. Literature Review: Reviewed 6 benchmark papers and identified the sub-25ms streaming latency research gap.\n' \
               '4. Architecture & PERT Schedule: Formulated dual-stage sidecar proxy architecture and 30-week milestone schedule.\n' \
               '5. Synopsis Submission: Formally prepared and submitted Project Synopsis for Group 50.'
    
    try:
        doc.save(out_docx_path)
        print(f'Successfully updated WPR docx at {out_docx_path}')
    except PermissionError:
        doc.save(fallback_path)
        print(f'Original file locked; successfully saved brief WPR docx at {fallback_path}')

if __name__ == '__main__':
    update_wpr()
