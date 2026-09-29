import json
import time
import pandas as pd
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

def test_stage2_real():
    df_fever = pd.read_csv("FEVER_NAACL2018_Fact_Verification.csv")
    df_halu = pd.read_csv("HaluEval_EMNLP2023_Hallucination_Benchmark.csv")
    
    pairs = []
    # 1. FEVER: 200 SUPPORTS (label 0), 200 REFUTES (label 1)
    for idx, row in df_fever.iterrows():
        is_refute = (row["gold_label"].strip().upper() == "REFUTES")
        pairs.append({
            "id": f"FEVER_{row['id']}",
            "premise": str(row["evidence"]).strip(),
            "claim": str(row["claim"]).strip(),
            "label": 1 if is_refute else 0,
            "label_name": "Refuted / Falsehood" if is_refute else "Supported / Fact",
            "source": "FEVER (NAACL 2018)"
        })
        
    # 2. HaluEval: 200 questions -> 200 Grounded (label 0) + 200 Hallucinated (label 1)
    for idx, row in df_halu.iterrows():
        q = str(row["question"]).strip()
        f_resp = str(row["factual_response"]).strip()
        h_resp = str(row["hallucinated_response"]).strip()
        domain = str(row.get("domain", "")).strip()
        
        premise = f"Context ({domain}): {q}" if domain else f"Context: {q}"
        
        # Grounded
        pairs.append({
            "id": f"HALU_{row['id']}_G",
            "premise": premise,
            "claim": f_resp,
            "label": 0,
            "label_name": "Grounded / Factual",
            "source": "HaluEval (EMNLP 2023)"
        })
        # Hallucinated
        pairs.append({
            "id": f"HALU_{row['id']}_H",
            "premise": premise,
            "claim": h_resp,
            "label": 1,
            "label_name": "Hallucinated / Contradiction",
            "source": "HaluEval (EMNLP 2023)"
        })
        
    print(f"Total Unique Stage 2 Pairs Assembled: {len(pairs)}")
    grounded_count = sum(1 for p in pairs if p["label"] == 0)
    hallu_count = sum(1 for p in pairs if p["label"] == 1)
    print(f"  • Grounded / Supported (0): {grounded_count}")
    print(f"  • Hallucinated / Refuted (1): {hallu_count}")
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model_name = "cross-encoder/nli-deberta-v3-small"
    print(f"\nLoading {model_name} on {device.upper()}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
    model = AutoModelForSequenceClassification.from_pretrained(model_name).to(device)
    model.eval()
    
    batch_size = 32
    y_true = np.array([p["label"] for p in pairs])
    all_probs = []
    
    t_start = time.perf_counter()
    for i in range(0, len(pairs), batch_size):
        batch = pairs[i:i + batch_size]
        premises = [b["premise"] for b in batch]
        claims = [b["claim"] for b in batch]
        
        inputs = tokenizer(premises, claims, return_tensors="pt", truncation=True, max_length=256, padding=True).to(device)
        with torch.no_grad():
            out = model(**inputs)
            probs = torch.softmax(out.logits, dim=-1).cpu().numpy()
            all_probs.extend(probs.tolist())
            
    elapsed = time.perf_counter() - t_start
    all_probs = np.array(all_probs)
    # Labels in cross-encoder/nli-deberta-v3-small: [0: contradiction, 1: entailment, 2: neutral]
    p_contra = all_probs[:, 0]
    p_entail = all_probs[:, 1]
    p_neutral = all_probs[:, 2]
    
    print(f"Inference completed in {elapsed:.2f} s ({elapsed/len(pairs)*1000:.2f} ms/pair)")
    
    # Test two standard decision rules:
    # Rule 1: Contradiction vs Entailment (p_contra > p_entail)
    # Rule 2: Non-Entailment (Entailment < 0.50 => Flagged)
    # Rule 3: Contradiction threshold (p_contra >= 0.50)
    
    rules = [
        ("Rule A (Contradiction > 0.50)", p_contra >= 0.50),
        ("Rule B (p_contra > p_entail)", p_contra > p_entail),
        ("Rule C (Non-Entailment: p_entail < 0.50)", p_entail < 0.50),
        ("Rule D (Argmax Contradiction)", np.argmax(all_probs, axis=-1) == 0)
    ]
    
    for r_name, pred_bool in rules:
        y_pred = pred_bool.astype(int)
        tp = int(np.sum((y_pred == 1) & (y_true == 1)))
        tn = int(np.sum((y_pred == 0) & (y_true == 0)))
        fp = int(np.sum((y_pred == 1) & (y_true == 0)))
        fn = int(np.sum((y_pred == 0) & (y_true == 1)))
        
        acc = (tp + tn) / len(y_true)
        rec = tp / max(1, (tp + fn))
        prec = tp / max(1, (tp + fp))
        f1 = 2 * prec * rec / max(1e-6, (prec + rec))
        fpr = fp / max(1, (fp + tn))
        
        print(f"\n--- {r_name} ---")
        print(f"TP (Hallucinations caught): {tp}/{hallu_count}, TN (Facts passed): {tn}/{grounded_count}, FP: {fp}, FN: {fn}")
        print(f"Accuracy: {acc*100:.2f}% | Recall: {rec*100:.2f}% | Precision: {prec*100:.2f}% | F1: {f1:.4f} | FPR: {fpr*100:.2f}%")

if __name__ == "__main__":
    test_stage2_real()
