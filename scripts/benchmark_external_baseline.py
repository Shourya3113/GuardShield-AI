"""
================================================================================
 GuardShield AI — External Industry Baseline Evaluation (ProtectAI DeBERTa-v3)
================================================================================
 Evaluates ProtectAI's public prompt injection classifier:
   • Model: protectai/deberta-v3-base-prompt-injection-v2
   • Total Parameters: 184.0M (86M backbone + 98M embeddings) vs GuardShield 142.6M (44.3M + 98.3M)
   • In-Distribution Test Split: data/processed/splits_v3/test_in_distribution.json (N=698)
   • Zero-Shot OOD Test Split: data/processed/splits_v3/test_out_of_distribution.json (N=500)
   • Granular Human DAN Jailbreaks (N=76) vs Template-Shift (N=174) Breakdown
   • Benign-Hard Diagnostic Suite (N=65)
   • XSTest v2 Benchmark (N=450: 250 Safe, 200 Contrast Unsafe)
 Exports: docs/01 Reports/table_external_baseline_protectai.json
================================================================================
"""

import os
import sys
import json
import time
import hashlib
import subprocess
from pathlib import Path
import numpy as np
import torch
import transformers
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

BASE_DIR = Path(__file__).resolve().parent.parent
SPLITS_DIR = BASE_DIR / "data" / "processed" / "splits_v3"
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "docs" / "01 Reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

MODEL_ID = "protectai/deberta-v3-base-prompt-injection-v2"

def get_git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(BASE_DIR), stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"

def compute_sha256(filepath):
    p = Path(filepath)
    if not p.is_file(): return None
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536): h.update(chunk)
    return h.hexdigest()

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
            probs = torch.softmax(outputs.logits, dim=-1)[0]
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

    result = {
        "split_name": split_name,
        "sample_count": len(data),
        "dataset_sha256": compute_sha256(split_path),
        "accuracy": round(float(acc), 4),
        "recall": round(float(rec), 4),
        "precision": round(float(prec), 4),
        "f1_score": round(float(f1), 4),
        "fpr": round(float(fpr), 4),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "latency_p50_ms": round(float(np.median(latencies)), 2),
        "latency_mean_ms": round(float(np.mean(latencies)), 2)
    }

    # Granular OOD breakdown if applicable
    if "OOD" in split_name:
        dan_indices = [i for i, d in enumerate(data) if "JailbreakBench" in d.get("source", "")]
        synth_indices = [i for i, d in enumerate(data) if d.get("label") == 1 and i not in dan_indices]
        
        dan_tp = sum(y_pred[i] for i in dan_indices)
        synth_tp = sum(y_pred[i] for i in synth_indices)
        
        dan_rec = dan_tp / len(dan_indices) if dan_indices else 0.0
        synth_rec = synth_tp / len(synth_indices) if synth_indices else 0.0
        
        result["granular_breakdown"] = {
            "human_dan_jailbreak_recall": round(float(dan_rec), 4),
            "human_dan_sample_count": len(dan_indices),
            "human_dan_tp": int(dan_tp),
            "template_shift_recall": round(float(synth_rec), 4),
            "template_shift_sample_count": len(synth_indices),
            "template_shift_tp": int(synth_tp)
        }
        print(f"  • Human DAN Recall:       {dan_rec*100:.2f}% ({dan_tp}/{len(dan_indices)})")
        print(f"  • Template-Shift Recall:  {synth_rec*100:.2f}% ({synth_tp}/{len(synth_indices)})")

    return result

def evaluate_benign_hard(model, tokenizer, device):
    benign_hard_path = DATA_DIR / "benign_hard_eval.json"
    if not benign_hard_path.is_file():
        return None
    with open(benign_hard_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    y_true = []
    y_pred = []
    print(f"\nEvaluating {MODEL_ID} on Benign-Hard Diagnostic Suite (N={len(data)})...")
    for item in data:
        prompt = item["prompt"]
        lbl = int(item.get("label", 0))
        y_true.append(lbl)
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(device)
        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)[0]
            pred = int(torch.argmax(probs).item())
        y_pred.append(pred)

    benign_indices = [i for i, lbl in enumerate(y_true) if lbl == 0]
    attack_indices = [i for i, lbl in enumerate(y_true) if lbl == 1]

    benign_fp = sum(y_pred[i] for i in benign_indices)
    benign_fpr = benign_fp / len(benign_indices) if benign_indices else 0.0

    attack_tp = sum(y_pred[i] for i in attack_indices)
    attack_rec = attack_tp / len(attack_indices) if attack_indices else 0.0

    correct = sum(1 for yt, yp in zip(y_true, y_pred) if yt == yp)
    acc = correct / len(data) if data else 0.0

    print(f"  • Benign Prompts (N={len(benign_indices)}): False Positive Rate = {benign_fpr*100:.2f}% ({benign_fp} false alarms)")
    print(f"  • Adversarial Injections (N={len(attack_indices)}): Recall = {attack_rec*100:.2f}% ({attack_tp} caught)")
    print(f"  • Overall Diagnostic Accuracy: {acc*100:.2f}%")

    return {
        "sample_count": len(data),
        "dataset_sha256": compute_sha256(benign_hard_path),
        "benign_sample_count": len(benign_indices),
        "false_positive_count": int(benign_fp),
        "false_positive_rate": round(float(benign_fpr), 4),
        "attack_sample_count": len(attack_indices),
        "attack_recall": round(float(attack_rec), 4),
        "attack_tp": int(attack_tp),
        "accuracy": round(float(acc), 4)
    }

def evaluate_xstest(model, tokenizer, device):
    xstest_path = DATA_DIR / "massive_benchmark" / "stage1_test_xstest.json"
    if not xstest_path.is_file():
        return None
    with open(xstest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    safe_prompts = [d for d in data if d.get("label") == 0]
    unsafe_prompts = [d for d in data if d.get("label") == 1]

    def test_subset(subset):
        preds = []
        for d in subset:
            inputs = tokenizer(d["prompt"], return_tensors="pt", truncation=True, max_length=512).to(device)
            with torch.no_grad():
                probs = torch.softmax(model(**inputs).logits, dim=-1)[0]
                preds.append(int(torch.argmax(probs).item()))
        return preds

    safe_preds = test_subset(safe_prompts)
    unsafe_preds = test_subset(unsafe_prompts)

    safe_fp = sum(safe_preds)
    safe_frr = safe_fp / len(safe_prompts) if safe_prompts else 0.0

    unsafe_tp = sum(unsafe_preds)
    unsafe_rec = unsafe_tp / len(unsafe_prompts) if unsafe_prompts else 0.0

    print(f"\nEvaluating {MODEL_ID} on XSTest v2 Benchmark (N={len(data)})...")
    print(f"  • Safe Prompts (N={len(safe_prompts)}): False Refusal Rate = {safe_frr*100:.2f}% ({safe_fp} false blocks)")
    print(f"  • Contrast Unsafe Prompts (N={len(unsafe_prompts)}): Recall = {unsafe_rec*100:.2f}% ({unsafe_tp} caught)")

    return {
        "sample_count": len(data),
        "dataset_sha256": compute_sha256(xstest_path),
        "safe_prompts_count": len(safe_prompts),
        "safe_false_refusal_rate": round(float(safe_frr), 4),
        "contrast_unsafe_count": len(unsafe_prompts),
        "contrast_unsafe_recall": round(float(unsafe_rec), 4)
    }

def run_external_benchmark():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading external baseline model: {MODEL_ID} on {device.upper()}...")

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
    benign_hard_res = evaluate_benign_hard(model, tokenizer, device)
    xstest_res = evaluate_xstest(model, tokenizer, device)

    output = {
        "metadata": {
            "model_name": MODEL_ID,
            "architecture": "DeBERTa-v3-base",
            "backbone_parameters": "86.0M",
            "embedding_parameters": "98.0M",
            "total_parameters": "184.0M",
            "comparison_notes": "ProtectAI DeBERTa-v3-base has 184M total params compared to GuardShield-AI's 142.6M (44.3M backbone + 98.3M embeddings). ProtectAI is zero-shot on these benchmarks; GuardShield was fine-tuned on the in-distribution training split.",
            "git_commit": get_git_commit(),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "device": device.upper(),
            "device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU",
            "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
            "torch_version": torch.__version__,
            "transformers_version": transformers.__version__,
            "batch_size": 1
        },
        "in_distribution": in_res,
        "out_of_distribution": ood_res,
        "benign_hard_control": benign_hard_res,
        "xstest_control": xstest_res
    }

    out_path = REPORTS_DIR / "table_external_baseline_protectai.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved external baseline report to {out_path}!")

if __name__ == "__main__":
    run_external_benchmark()
