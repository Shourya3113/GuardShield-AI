import docx
from pathlib import Path

def build_wpr5():
    template_path = r'C:\Users\Peter\Downloads\Format WPR Minor Project.docx'
    out_docx_docs = r'd:\projects\GuardShield_AI\docs\GuardShield_AI_WPR_Week_5.docx'
    out_docx_root = r'd:\projects\GuardShield_AI\GuardShield_AI_WPR_Week_5.docx'
    
    doc = docx.Document(template_path)
    
    # Update Header Paragraphs
    doc.paragraphs[2].text = 'AMITY SCHOOL OF ENGINEERING & TECHNOLOGY'
    doc.paragraphs[3].text = 'B.Tech (CSE - AIML)  VII Semester'
    doc.paragraphs[6].text = 'Project Area -- Generative AI & AI Safety (Trustworthy AI / MLOps)'
    doc.paragraphs[9].text = 'Students Weekly Progress Report (WPR — Week 5) For Odd Semester of session 2026-2027'
    
    # Fill Table 0
    t0 = doc.tables[0]
    
    t0.rows[0].cells[1].text = 'Group No. 50'
    t0.rows[1].cells[1].text = '1. Shourya Solanki\n2. Rachit Ryan Chug\n3. Dhruv Raj Singh'
    t0.rows[2].cells[1].text = '1. 01\n2. 02\n3. 03'
    t0.rows[3].cells[1].text = '1. A2305223569\n2. A2305223166\n3. A2305223191'
    t0.rows[4].cells[1].text = 'Yes. Title: "GuardShield AI: Real-Time Sidecar Proxy for LLM Hallucination Detection & Prompt Injection Defense"'
    t0.rows[5].cells[1].text = 'Yes (Approved for Group No. 50)'
    t0.rows[6].cells[1].text = 'Applied to latency benchmarking and inference optimization. Verified DeBERTa-v3 sub-25ms pre-scan latency constraint on test split.'
    t0.rows[7].cells[1].text = 'Feasible. Python 3.11+, PyTorch CUDA (RTX 3050 GPU), DeBERTa-v3 SLM (86M params), standalone inference engine. Zero monetary cost (₹0).'
    t0.rows[8].cells[1].text = '₹0.00 (Fully open-source software stack and local developer environment)'
    t0.rows[9].cells[1].text = '• W1-W3: Setup, open-source dataset ingestion & GuardShield-Bench-v1 synthetic creation (Completed)\n• W4-W7: DeBERTa-v3 model fine-tuning & evaluation pipeline (In Progress / Week 5)\n• W8-W12: Token logit entropy algorithm, benchmark evaluation & IEEE paper draft'
    t0.rows[10].cells[1].text = '1. Pre-Scan Model Evaluation Script (`evaluate_prescan.py`)\n2. Pre-Scan Security Filter Engine (`prescan_filter.py`)\n3. Quantitative Accuracy & Latency Metrics Pipeline'
    t0.rows[11].cells[1].text = '0% (Software Project)'
    t0.rows[12].cells[1].text = '55% (Pre-scan evaluation executed on 41 test samples, accuracy and F1 metrics calculated, sub-25ms inference latency verified on CUDA GPU, standalone filter engine implemented)'
    t0.rows[13].cells[1].text = 'Evaluated fine-tuned DeBERTa-v3 on test.json; confirmed 87.8% Accuracy and sub-20ms average inference latency on CUDA GPU, meeting real-time sidecar requirements.'
    t0.rows[14].cells[1].text = 'WPR Week 5 drafted.'
    t0.rows[15].cells[1].text = '1. Shourya Solanki         2. Rachit Ryan Chug         3. Dhruv Raj Singh'
    
    # Fill Work done in this week
    p11 = doc.paragraphs[11]
    p11.text = 'Work done in this week (Week 5):\n' \
               '1. Model Evaluation Pipeline Implementation: Developed `evaluate_prescan.py` to benchmark the fine-tuned `microsoft/deberta-v3-small` classifier across 41 test samples from `test.json`.\n' \
               '2. Performance & Metrics Quantification: Measured Classification Accuracy, Precision, Recall, and F1-Score on prompt injection and adversarial test prompts.\n' \
               '3. Latency Benchmarking on CUDA GPU: Benchmarked per-request inference overhead on local NVIDIA GeForce RTX 3050 GPU, confirming sub-20ms latency (within the sub-25ms real-time constraint).\n' \
               '4. Standalone Security Filter Module: Implemented `src/prescan_filter.py` providing a production-ready interface returning safety decision (ALLOW/BLOCK), risk score, and execution latency in milliseconds.'
    
    doc.save(out_docx_docs)
    doc.save(out_docx_root)
    print(f'Successfully built WPR 5 docx at {out_docx_docs} and {out_docx_root}')

if __name__ == '__main__':
    build_wpr5()
