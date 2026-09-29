import os
import sys
import json
import time
import torch
import numpy as np
from pathlib import Path
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src"))

from prescan_filter import PreScanSecurityFilter
from nli_verifier import WindowedNLIVerifier

REPORTS_DIR = BASE_DIR / "docs" / "01 Reports"
SPLITS_DIR = BASE_DIR / "data" / "processed" / "splits_v3"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def export_stage1_eval(split_file, split_name, out_filename):
    print(f"\nEvaluating Stage 1 on {split_name} ({split_file})...")
    engine = PreScanSecurityFilter()
    
    with open(SPLITS_DIR / split_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    records = []
    y_true, y_pred, latencies = [], [], []
    
    for idx, item in enumerate(data):
        prompt = item["prompt"]
        lbl = int(item["label"])
        res = engine.inspect_prompt(prompt)
        
        pred = 1 if not res["is_safe"] else 0
        correct = (pred == lbl)
        
        y_true.append(lbl)
        y_pred.append(pred)
        latencies.append(res["latency_ms"])
        
        records.append({
            "index": idx,
            "prompt": prompt,
            "source": item.get("source", "Unknown"),
            "true_label": lbl,
            "true_name": "Attack" if lbl == 1 else "Safe",
            "predicted_label": pred,
            "predicted_name": "Attack" if pred == 1 else "Safe",
            "risk_score": res["risk_score"],
            "decision": res["decision"],
            "latency_ms": res["latency_ms"],
            "correct": correct
        })
        
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    fpr = fp / (fp + tn)
    
    payload = {
        "metadata": {
            "split_name": split_name,
            "evaluated_file": split_file,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "sample_count": len(records),
            "model_path": str(engine.model_dir),
            "decision_rule": "risk_score >= 0.50 (Block as Attack) with sliding-window chunking"
        },
        "metrics": {
            "accuracy": round(float(acc), 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1_score": round(float(f1), 4),
            "fpr": round(float(fpr), 4),
            "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
            "latency_p50_ms": round(float(np.median(latencies)), 2),
            "latency_mean_ms": round(float(np.mean(latencies)), 2),
            "latency_p95_ms": round(float(np.percentile(latencies, 95)), 2)
        },
        "predictions": records
    }
    
    out_path = REPORTS_DIR / out_filename
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Saved {len(records)} raw predictions to {out_path}")
    print(f"Accuracy: {acc*100:.2f}% | Recall: {rec*100:.2f}% | Precision: {prec*100:.2f}% | FPR: {fpr*100:.2f}%")
    return payload

def export_stage2_eval():
    print("\nEvaluating Stage 2 on Authentic 800 Factuality Pairs (FEVER + HaluEval)...")
    verifier = WindowedNLIVerifier()
    
    with open(SPLITS_DIR / "fever_eval_400.json", "r", encoding="utf-8") as f:
        fever_data = json.load(f)
    with open(SPLITS_DIR / "halueval_eval_400.json", "r", encoding="utf-8") as f:
        halu_data = json.load(f)
        
    combined = fever_data + halu_data
    records = []
    y_true, y_pred, latencies = [], [], []
    
    for idx, item in enumerate(combined):
        premise = item["premise"]
        claim = item["claim"]
        lbl = int(item["label"]) # 1 = Contradiction / Hallucination, 0 = Supported
        
        res = verifier.verify_entailment(premise, claim)
        p_contra = res["contradiction_prob"]
        pred = 1 if p_contra >= 0.50 else 0
        correct = (pred == lbl)
        
        y_true.append(lbl)
        y_pred.append(pred)
        latencies.append(res["latency_ms"])
        
        records.append({
            "index": idx,
            "id": item.get("id", f"PAIR_{idx}"),
            "source": item.get("source", "Unknown"),
            "premise": premise,
            "claim": claim,
            "true_label": lbl,
            "true_name": "Contradiction / Hallucination" if lbl == 1 else "Supported / Fact",
            "predicted_label": pred,
            "predicted_name": "Contradiction / Hallucination" if pred == 1 else "Supported / Fact",
            "contradiction_prob": p_contra,
            "entailment_prob": res["entailment_prob"],
            "latency_ms": res["latency_ms"],
            "correct": correct
        })
        
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    fpr = fp / (fp + tn)
    
    payload = {
        "metadata": {
            "suite_name": "Authentic Multi-Source Fact Grounding Suite (FEVER + HaluEval)",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "sample_count": len(records),
            "model_name": verifier.model_name,
            "decision_rule": "contradiction_prob >= 0.50 (Flagged as Hallucination)"
        },
        "metrics": {
            "accuracy": round(float(acc), 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1_score": round(float(f1), 4),
            "fpr": round(float(fpr), 4),
            "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
            "latency_p50_ms": round(float(np.median(latencies)), 2),
            "latency_mean_ms": round(float(np.mean(latencies)), 2),
            "latency_p95_ms": round(float(np.percentile(latencies, 95)), 2)
        },
        "predictions": records
    }
    
    out_path = REPORTS_DIR / "raw_eval_stage2_factuality_800.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Saved {len(records)} raw predictions to {out_path}")
    print(f"Accuracy: {acc*100:.2f}% | Recall: {rec*100:.2f}% | Precision: {prec*100:.2f}% | FPR: {fpr*100:.2f}%")
    return payload

if __name__ == "__main__":
    export_stage1_eval("test_in_distribution.json", "In-Distribution Test (698)", "raw_eval_in_distribution_test_698.json")
    export_stage1_eval("test_out_of_distribution.json", "Zero-Shot OOD Test (500)", "raw_eval_out_of_distribution_500.json")
    export_stage2_eval()
    print("\nAll raw evaluation outputs successfully generated and stored in docs/01 Reports/!")
