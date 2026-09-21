import docx
from pathlib import Path

def build_wpr4():
    template_path = r'C:\Users\Peter\Downloads\Format WPR Minor Project.docx'
    out_docx_docs = r'd:\projects\GuardShield_AI\docs\GuardShield_AI_WPR_Week_4.docx'
    out_docx_root = r'd:\projects\GuardShield_AI\GuardShield_AI_WPR_Week_4.docx'
    
    doc = docx.Document(template_path)
    
    # Update Header Paragraphs
    doc.paragraphs[2].text = 'AMITY SCHOOL OF ENGINEERING & TECHNOLOGY'
    doc.paragraphs[3].text = 'B.Tech (CSE - AIML)  VII Semester'
    doc.paragraphs[6].text = 'Project Area -- Generative AI & AI Safety (Trustworthy AI / MLOps)'
    doc.paragraphs[9].text = 'Students Weekly Progress Report (WPR — Week 4) For Odd Semester of session 2026-2027'
    
    # Fill Table 0
    t0 = doc.tables[0]
    
    t0.rows[0].cells[1].text = 'Group No. 50'
    t0.rows[1].cells[1].text = '1. Shourya Solanki\n2. Rachit Ryan Chug\n3. Dhruv Raj Singh'
    t0.rows[2].cells[1].text = '1. 01\n2. 02\n3. 03'
    t0.rows[3].cells[1].text = '1. A2305223569\n2. A2305223166\n3. A2305223191'
    t0.rows[4].cells[1].text = 'Yes. Title: "GuardShield AI: Real-Time Sidecar Proxy for LLM Hallucination Detection & Prompt Injection Defense"'
    t0.rows[5].cells[1].text = 'Yes (Approved for Group No. 50)'
    t0.rows[6].cells[1].text = 'Applied to model fine-tuning. Utilized cross-entropy loss and DeBERTa-v3 multi-class classification head for prompt injection detection.'
    t0.rows[7].cells[1].text = 'Feasible. Python 3.11+, PyTorch CUDA (RTX 3050 GPU), DeBERTa-v3-small (86M SLM), Hugging Face Trainer. Zero monetary cost (₹0).'
    t0.rows[8].cells[1].text = '₹0.00 (Fully open-source software stack and local developer environment)'
    t0.rows[9].cells[1].text = '• W1-W3: Setup, open-source dataset ingestion & GuardShield-Bench-v1 synthetic creation (Completed)\n• W4-W7: DeBERTa-v3 model fine-tuning & evaluation pipeline (In Progress / Week 4)\n• W8-W12: Token logit entropy algorithm, benchmark evaluation & IEEE paper draft'
    t0.rows[10].cells[1].text = '1. Pre-Scan DeBERTa-v3 Model Fine-Tuning Pipeline (`train_prescan.py`)\n2. PyTorch Dataset Loader & Data Collator with Padding\n3. Hugging Face Trainer Loop & Checkpointing (`models/deberta_v3_prescan/`)'
    t0.rows[11].cells[1].text = '0% (Software Project)'
    t0.rows[12].cells[1].text = '45% (Pre-scan DeBERTa-v3 classifier fine-tuning script implemented, training pass executed on CUDA GPU, model checkpoints saved)'
    t0.rows[13].cells[1].text = 'Configured PyTorch Trainer for microsoft/deberta-v3-small; executed fine-tuning on 320 train samples; verified loss convergence and checkpoint saving on CUDA GPU.'
    t0.rows[14].cells[1].text = 'WPR Week 4 drafted.'
    t0.rows[15].cells[1].text = '1. Shourya Solanki         2. Rachit Ryan Chug         3. Dhruv Raj Singh'
    
    # Fill Work done in this week
    p11 = doc.paragraphs[11]
    p11.text = 'Work done in this week (Week 4):\n' \
               '1. Pre-Scan Fine-Tuning Script Implementation: Developed `train_prescan.py` using PyTorch & Hugging Face `Trainer` to fine-tune `microsoft/deberta-v3-small` (86M SLM) on `train.json`.\n' \
               '2. Training Architecture & Loss Configuration: Configured sequence classification head (2 classes: Safe vs. Injection/Jailbreak), AdamW optimizer (learning rate 2e-5), and cross-entropy loss.\n' \
               '3. Training Execution on CUDA GPU: Executed fine-tuning on local NVIDIA GeForce RTX 3050 GPU, logging training loss across steps.\n' \
               '4. Model Checkpointing & Artifact Saving: Saved fine-tuned model weights and tokenizer configuration under `models/deberta_v3_prescan/`.'
    
    doc.save(out_docx_docs)
    doc.save(out_docx_root)
    print(f'Successfully built WPR 4 docx at {out_docx_docs} and {out_docx_root}')

if __name__ == '__main__':
    build_wpr4()
