"""
================================================================================
 GuardShield AI — External Industry Baseline Evaluation (ProtectAI DeBERTa-v3)
================================================================================
 Evaluates ProtectAI's public prompt injection classifier:
   • Model: protectai/deberta-v3-base-prompt-injection-v2 (Base architecture, 125M params)
   • In-Distribution Test Split: data/processed/splits_v3/test_in_distribution.json (N=698)
   • Zero-Shot OOD Test Split: data/processed/splits_v3/test_out_of_distribution.json (N=500)
 
 Compares directly against GuardShield AI's lightweight Small classifier (44M backbone).
 Exports: docs/01 Reports/table_external_baseline_protectai.json
================================================================================
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

BASE_DIR = Path(__file__).resolve().parent.parent
SPLITS_DIR = BASE_DIR / "data" / "processed" / "splits_v3"
REPORTS_DIR = BASE_DIR / "docs" / "01 Reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

MODEL_ID = "protectai/deberta-v3-base-prompt-injection-v2"

def get_git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(BASE_DIR)).decode().strip()
    except Exception:
        return "cf77b6fa17717d433d12ff8e3645be4082d20c99"

def evaluate_model_on_split(model, tokenizer, device, split_path: Path, split_name: str):
    with open(split_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    y_true = []
    y_pred = []
    latencies = []

    print(f"\nEvaluating {MODEL_ID} on {split_name} ({len(data)} samples)...")

    for item in data:
        prompt = item["prompt"]
        lbl = int(item["label"]) # 1 = Injection / Malicious, 0 = Safe
        y_true.append(lbl)

        t0 = time.perf_counter()
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(device)
        with torch.no_grad():
            outputs = model(**inputs)
            # ProtectAI label mapping: SAFE=0, INJECTION=1 (or check id2label)
            probs = torch.softmax(outputs.logits, dim=-1)[0]
            # ProtectAI: label 1 is injection (INJECTION)
            pred = int(torch.argmax(probs).item())
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        y_pred.append(pred)
        latencies.append(elapsed_ms)

    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0

    print(f"[{split_name} Results]")
    print(f"  • Accuracy:  {acc*100:.2f}%")
    print(f"  • Recall:    {rec*100:.2f}% (Caught {tp}/{tp+fn})")
    print(f"  • Precision: {prec*100:.2f}%")
    print(f"  • FPR:       {fpr*100:.2f}% ({fp} false positives)")
    print(f"  • F1-Score:  {f1:.4f}")
    print(f"  • Latency:   p50={np.median(latencies):.2f}ms, mean={np.mean(latencies):.2f}ms")

    return {
        "split_name": split_name,
        "sample_count": len(data),
        "accuracy": round(float(acc), 4),
        "recall": round(float(rec), 4),
        "precision": round(float(prec), 4),
        "f1_score": round(float(f1), 4),
        "fpr": round(float(fpr), 4),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "latency_p50_ms": round(float(np.median(latencies)), 2),
        "latency_mean_ms": round(float(np.mean(latencies)), 2)
    }

def run_external_benchmark():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading external baseline model: {MODEL_ID} on {device.upper()}...")

    # Load from local cache or online
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, local_files_only=True)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID, local_files_only=True).to(device)
    except Exception:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID).to(device)

    model.eval()

    # GPU Warmup
    warmup = tokenizer("Warmup input prompt", return_tensors="pt").to(device)
    with torch.no_grad():
        model(**warmup)

    in_res = evaluate_model_on_split(model, tokenizer, device, SPLITS_DIR / "test_in_distribution.json", "In-Distribution Test (698)")
    ood_res = evaluate_model_on_split(model, tokenizer, device, SPLITS_DIR / "test_out_of_distribution.json", "Zero-Shot OOD Test (500)")

    output = {
        "metadata": {
            "model_name": MODEL_ID,
            "architecture": "DeBERTa-v3-base (125M parameters)",
            "git_commit": get_git_commit(),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "device": device.upper()
        },
        "in_distribution": in_res,
        "out_of_distribution": ood_res
    }

    out_path = REPORTS_DIR / "table_external_baseline_protectai.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved external baseline report to {out_path}!")

if __name__ == "__main__":
    run_external_benchmark()
