import os
import sys
import json
import time
import hashlib
import subprocess
import torch
import transformers
import numpy as np
from pathlib import Path
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src"))

from prescan_filter import PreScanSecurityFilter
from nli_verifier import WindowedNLIVerifier

REPORTS_DIR = BASE_DIR / "docs" / "01 Reports"
SPLITS_DIR = BASE_DIR / "data" / "processed" / "splits_v3"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def get_git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(BASE_DIR), stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"

def compute_sha256(filepath):
    p = Path(filepath)
    if not p.is_file():
        return None
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

GIT_COMMIT_HASH = get_git_commit()
STAGE1_WEIGHTS_PATH = BASE_DIR / "models" / "deberta_v3_prescan_v3" / "model.safetensors"
STAGE1_WEIGHTS_SHA256 = compute_sha256(STAGE1_WEIGHTS_PATH)

def export_stage1_eval(split_file, split_name, out_filename):
    print(f"\nEvaluating Stage 1 on {split_name} ({split_file})...")
    engine = PreScanSecurityFilter()
    
    dataset_path = SPLITS_DIR / split_file
    with open(dataset_path, "r", encoding="utf-8") as f:
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
            "git_commit": GIT_COMMIT_HASH,
            "evaluated_file": split_file,
            "dataset_sha256": compute_sha256(dataset_path),
            "weights_sha256": STAGE1_WEIGHTS_SHA256,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "sample_count": len(records),
            "model_path": str(engine.model_dir),
            "decision_rule": "risk_score >= 0.50 (Block as Attack) with sliding-window chunking",
            "device": engine.device.upper(),
            "device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU",
            "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
            "torch_version": torch.__version__,
            "transformers_version": transformers.__version__,
            "batch_size": 1
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
    print("\nEvaluating Stage 2 on Authentic 800 Factuality Pairs (FEVER + HaluEval) using windowed verify_claim...")
    verifier = WindowedNLIVerifier()
    
    fever_path = SPLITS_DIR / "fever_eval_400.json"
    halu_path = SPLITS_DIR / "halueval_eval_400.json"
    
    with open(fever_path, "r", encoding="utf-8") as f:
        fever_data = json.load(f)
    with open(halu_path, "r", encoding="utf-8") as f:
        halu_data = json.load(f)
        
    combined = fever_data + halu_data
    records = []
    y_true, y_pred, p_contras, latencies = [], [], [], []
    
    # 3-way tracking
    three_way_matrix = {
        "supported": {"entailed": 0, "neutral": 0, "contradiction": 0},
        "hallucination": {"entailed": 0, "neutral": 0, "contradiction": 0}
    }
    
    fever_true, fever_pred, fever_contra = [], [], []
    halu_true, halu_pred, halu_contra = [], [], []
    
    for idx, item in enumerate(combined):
        premise = item["premise"]
        claim = item["claim"]
        lbl = int(item["label"]) # 1 = Contradiction / Hallucination, 0 = Supported
        src = item.get("source", "Unknown")
        
        res = verifier.verify_claim(premise, claim)
        # Disaggregated: Hard Hallucination flagged when contradiction >= 0.50
        pred = 1 if res["is_hallucination"] else 0
        correct = (pred == lbl)
        
        p_c = float(res.get("contradiction_prob", 0.0))
        y_true.append(lbl)
        y_pred.append(pred)
        p_contras.append(p_c)
        latencies.append(res["latency_ms"])
        
        # Track 3-way
        dec = res.get("decision", "UNKNOWN")
        target_key = "hallucination" if lbl == 1 else "supported"
        if dec == "FACTUAL_ENTAILMENT":
            three_way_matrix[target_key]["entailed"] += 1
        elif dec == "UNVERIFIED_NEUTRAL":
            three_way_matrix[target_key]["neutral"] += 1
        elif dec == "HALLUCINATION_CONTRADICTION":
            three_way_matrix[target_key]["contradiction"] += 1
            
        if "FEVER" in src:
            fever_true.append(lbl)
            fever_pred.append(pred)
            fever_contra.append(p_c)
        else:
            halu_true.append(lbl)
            halu_pred.append(pred)
            halu_contra.append(p_c)
        
        records.append({
            "index": idx,
            "id": item.get("id", f"PAIR_{idx}"),
            "source": src,
            "premise": premise,
            "claim": claim,
            "true_label": lbl,
            "true_name": "Contradiction / Hallucination" if lbl == 1 else "Supported / Fact",
            "predicted_label": pred,
            "predicted_name": "Contradiction / Hallucination" if pred == 1 else "Supported / Fact",
            "decision": dec,
            "is_hallucination": res["is_hallucination"],
            "is_contradiction": res.get("is_contradiction", False),
            "is_unverified": res.get("is_unverified", False),
            "contradiction_prob": res.get("contradiction_prob", 0.0),
            "entailment_prob": res.get("entailment_prob", 0.0),
            "neutral_prob": res.get("neutral_prob", 0.0),
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
    auroc = roc_auc_score(y_true, p_contras)
    
    # Sub-suite statistics
    fever_acc = accuracy_score(fever_true, fever_pred)
    fever_rec = recall_score(fever_true, fever_pred, zero_division=0)
    fever_prec = precision_score(fever_true, fever_pred, zero_division=0)
    fever_cm = confusion_matrix(fever_true, fever_pred).ravel()
    fever_fpr = fever_cm[1] / (fever_cm[1] + fever_cm[0])
    fever_auroc = roc_auc_score(fever_true, fever_contra)
    
    halu_acc = accuracy_score(halu_true, halu_pred)
    halu_rec = recall_score(halu_true, halu_pred, zero_division=0)
    halu_prec = precision_score(halu_true, halu_pred, zero_division=0)
    halu_cm = confusion_matrix(halu_true, halu_pred).ravel()
    halu_fpr = halu_cm[1] / (halu_cm[1] + halu_cm[0])
    halu_auroc = roc_auc_score(halu_true, halu_contra)
    
    payload = {
        "metadata": {
            "suite_name": "Authentic Multi-Source Fact Grounding Suite (FEVER + HaluEval)",
            "git_commit": GIT_COMMIT_HASH,
            "dataset_fever_sha256": compute_sha256(fever_path),
            "dataset_halueval_sha256": compute_sha256(halu_path),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "sample_count": len(records),
            "model_name": verifier.model_name,
            "decision_rule": "Windowed verify_claim: Disaggregated Contradiction (p_contra >= 0.50 flags hallucination); Neutral treated as UNVERIFIED_NEUTRAL rather than conflated with hallucination.",
            "device": verifier.device.upper(),
            "device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU",
            "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
            "torch_version": torch.__version__,
            "transformers_version": transformers.__version__,
            "batch_size": 1
        },
        "metrics": {
            "accuracy": round(float(acc), 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1_score": round(float(f1), 4),
            "fpr": round(float(fpr), 4),
            "auroc": round(float(auroc), 4),
            "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
            "latency_p50_ms": round(float(np.median(latencies)), 2),
            "latency_mean_ms": round(float(np.mean(latencies)), 2),
            "latency_p95_ms": round(float(np.percentile(latencies, 95)), 2)
        },
        "three_way_distribution": three_way_matrix,
        "per_source_breakdown": {
            "FEVER (NAACL 2018)": {
                "sample_count": len(fever_true),
                "accuracy": round(float(fever_acc), 4),
                "recall": round(float(fever_rec), 4),
                "precision": round(float(fever_prec), 4),
                "fpr": round(float(fever_fpr), 4),
                "auroc": round(float(fever_auroc), 4),
                "confusion_matrix": {"tn": int(fever_cm[0]), "fp": int(fever_cm[1]), "fn": int(fever_cm[2]), "tp": int(fever_cm[3])}
            },
            "HaluEval (EMNLP 2023)": {
                "sample_count": len(halu_true),
                "accuracy": round(float(halu_acc), 4),
                "recall": round(float(halu_rec), 4),
                "precision": round(float(halu_prec), 4),
                "fpr": round(float(halu_fpr), 4),
                "auroc": round(float(halu_auroc), 4),
                "confusion_matrix": {"tn": int(halu_cm[0]), "fp": int(halu_cm[1]), "fn": int(halu_cm[2]), "tp": int(halu_cm[3])}
            }
        },
        "predictions": records
    }
    
    out_path = REPORTS_DIR / "raw_eval_stage2_factuality_800.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Saved {len(records)} raw predictions to {out_path}")
    print(f"Overall Accuracy: {acc*100:.2f}% | Recall: {rec*100:.2f}% | Precision: {prec*100:.2f}% | FPR: {fpr*100:.2f}% | AUROC: {auroc:.4f}")
    print(f"FEVER: Acc={fever_acc*100:.2f}%, Rec={fever_rec*100:.2f}%, FPR={fever_fpr*100:.2f}%, AUROC={fever_auroc:.4f}")
    print(f"HaluEval: Acc={halu_acc*100:.2f}%, Rec={halu_rec*100:.2f}%, FPR={halu_fpr*100:.2f}%, AUROC={halu_auroc:.4f}")
    return payload

if __name__ == "__main__":
    export_stage1_eval("test_in_distribution.json", "In-Distribution Test (698)", "raw_eval_in_distribution_test_698.json")
    export_stage1_eval("test_out_of_distribution.json", "Zero-Shot OOD Test (500)", "raw_eval_out_of_distribution_500.json")
    export_stage2_eval()
    print("\nAll raw evaluation outputs successfully generated and stored in docs/01 Reports/!")
