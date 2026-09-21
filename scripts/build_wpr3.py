import docx
from pathlib import Path

def build_wpr3():
    template_path = r'C:\Users\Peter\Downloads\Format WPR Minor Project.docx'
    out_docx_docs = r'd:\projects\GuardShield_AI\docs\GuardShield_AI_WPR_Week_3.docx'
    out_docx_root = r'd:\projects\GuardShield_AI\GuardShield_AI_WPR_Week_3.docx'
    
    doc = docx.Document(template_path)
    
    # Update Header Paragraphs
    doc.paragraphs[2].text = 'AMITY SCHOOL OF ENGINEERING & TECHNOLOGY'
    doc.paragraphs[3].text = 'B.Tech (CSE - AIML)  VII Semester'
    doc.paragraphs[6].text = 'Project Area -- Generative AI & AI Safety (Trustworthy AI / MLOps)'
    doc.paragraphs[9].text = 'Students Weekly Progress Report (WPR — Week 3) For Odd Semester of session 2026-2027'
    
    # Fill Table 0
    t0 = doc.tables[0]
    
    t0.rows[0].cells[1].text = 'Group No. 50'
    t0.rows[1].cells[1].text = '1. Shourya Solanki\n2. Rachit Ryan Chug\n3. Dhruv Raj Singh'
    t0.rows[2].cells[1].text = '1. 01\n2. 02\n3. 03'
    t0.rows[3].cells[1].text = '1. A2305223569\n2. A2305223166\n3. A2305223191'
    t0.rows[4].cells[1].text = 'Yes. Title: "GuardShield AI: Real-Time Sidecar Proxy for LLM Hallucination Detection & Prompt Injection Defense"'
    t0.rows[5].cells[1].text = 'Yes (Approved for Group No. 50)'
    t0.rows[6].cells[1].text = 'Applied to synthetic dataset design. Incorporated Base64, ROT13, and Hinglish adversarial obfuscation attack vectors.'
    t0.rows[7].cells[1].text = 'Feasible. Python 3.11+, PyTorch CUDA (RTX 3050 GPU), DeBERTa-v3-small (86M SLM), Hugging Face Trainer. Zero monetary cost (₹0).'
    t0.rows[8].cells[1].text = '₹0.00 (Fully open-source software stack and local developer environment)'
    t0.rows[9].cells[1].text = '• W1-W3: Setup, open-source dataset ingestion & GuardShield-Bench-v1 synthetic creation (Completed / Week 3)\n• W4-W7: DeBERTa-v3 model fine-tuning & preprocessing pipeline\n• W8-W12: Token logit entropy algorithm, benchmark evaluation & IEEE paper draft'
    t0.rows[10].cells[1].text = '1. Obfuscated Synthetic Dataset Generator (Base64/ROT13/Hinglish)\n2. Dataset Splitting Pipeline (80% Train, 10% Val, 10% Test)\n3. Pre-Scan DeBERTa-v3 Multi-Class Classifier Initialization'
    t0.rows[11].cells[1].text = '0% (Software Project)'
    t0.rows[12].cells[1].text = '35% (Synthetic dataset generation, 401 records created, 80/10/10 split prepared, DeBERTa-v3 GPU initialization verified)'
    t0.rows[13].cells[1].text = 'Generated GuardShield-Bench-v1 (401 synthetic obfuscated records); created train (320), val (40), test (41) splits; verified DeBERTa-v3 forward-pass on CUDA GPU.'
    t0.rows[14].cells[1].text = 'WPR Week 3 drafted.'
    t0.rows[15].cells[1].text = '1. Shourya Solanki         2. Rachit Ryan Chug         3. Dhruv Raj Singh'
    
    # Fill Work done in this week
    p11 = doc.paragraphs[11]
    p11.text = 'Work done in this week (Week 3):\n' \
               '1. GuardShield-Bench-v1 Synthetic Dataset Creation: Built `obfuscation_generator.py` applying Base64, ROT13, and Hinglish code-mixing to benchmark prompt injections, producing 401 standardized records.\n' \
               '2. Train/Val/Test Dataset Splitting: Implemented `prepare_splits.py` dividing dataset into 80% Train (320 items), 10% Validation (40 items), and 10% Test (41 items) under `data/processed/splits/`.\n' \
               '3. DeBERTa-v3 Model Initialization: Developed `model_init.py` initializing Hugging Face `microsoft/deberta-v3-small` (86M parameters) on local NVIDIA RTX 3050 CUDA GPU.\n' \
               '4. Baseline Forward-Pass Verification: Tested model tokenizer and classification logits, confirming pipeline readiness for fine-tuning.'
    
    doc.save(out_docx_docs)
    doc.save(out_docx_root)
    print(f'Successfully built WPR 3 docx at {out_docx_docs} and {out_docx_root}')

if __name__ == '__main__':
    build_wpr3()
