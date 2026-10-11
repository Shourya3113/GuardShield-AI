"""
================================================================================
 GuardShield AI — TF-IDF + Logistic Regression Baseline Reproducibility
================================================================================
 Reproduces the comparative baseline:
   • Model: TfidfVectorizer (ngram_range=(1, 2), max_features=10000) + LogisticRegression
   • Training Split: data/processed/splits_v3/train.json
   • In-Distribution Test: data/processed/splits_v3/test_in_distribution.json (N=698)
   • Zero-Shot OOD Test: data/processed/splits_v3/test_out_of_distribution.json (N=500)
   • Evaluates granular DAN (JailbreakBench) vs Template-Shift OOD degradation.
================================================================================
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

BASE_DIR = Path(__file__).resolve().parent.parent
SPLITS_DIR = BASE_DIR / "data" / "processed" / "splits_v3"
REPORTS_DIR = BASE_DIR / "docs" / "01 Reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

import hashlib

def compute_sha256(filepath):
    p = Path(filepath)
    if not p.is_file(): return None
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536): h.update(chunk)
    return h.hexdigest()

def get_git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(BASE_DIR), stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"

def run_tfidf_baseline():
    print("\n" + "=" * 80)
    print("  EVALUATING TF-IDF + LOGISTIC REGRESSION BASELINE ON SPLITS V3")
    print("=" * 80)

    # 1. Load Training Data
    train_path = SPLITS_DIR / "train.json"
    with open(train_path, "r", encoding="utf-8") as f:
        train_data = json.load(f)

    X_train = [item["prompt"] for item in train_data]
    y_train = [int(item["label"]) for item in train_data]

    print(f"Loaded {len(X_train)} training prompts. Fitting TF-IDF vectorizer...")
    t0 = time.perf_counter()
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=10000, sublinear_tf=True)
    X_train_vec = vectorizer.fit_transform(X_train)
    
    clf = LogisticRegression(max_iter=1000, C=1.0, random_state=42)
    clf.fit(X_train_vec, y_train)
    fit_time = round((time.perf_counter() - t0), 2)
    print(f"Model trained in {fit_time}s.")

    # 2. Evaluate In-Distribution Test Set (698 samples)
    in_path = SPLITS_DIR / "test_in_distribution.json"
    with open(in_path, "r", encoding="utf-8") as f:
        in_dist_data = json.load(f)

    X_in = [item["prompt"] for item in in_dist_data]
    y_in = [int(item["label"]) for item in in_dist_data]
    X_in_vec = vectorizer.transform(X_in)
    y_in_pred = clf.predict(X_in_vec)

    in_acc = accuracy_score(y_in, y_in_pred)
    in_rec = recall_score(y_in, y_in_pred, zero_division=0)
    in_prec = precision_score(y_in, y_in_pred, zero_division=0)
    in_f1 = f1_score(y_in, y_in_pred, zero_division=0)

    print(f"\n[In-Distribution Test (N={len(y_in)})]")
    print(f"  • Accuracy:  {in_acc*100:.2f}%")
    print(f"  • Recall:    {in_rec*100:.2f}%")
    print(f"  • Precision: {in_prec*100:.2f}%")
    print(f"  • F1-Score:  {in_f1:.4f}")

    # 3. Evaluate Zero-Shot Out-of-Distribution Test Set (500 samples)
    ood_path = SPLITS_DIR / "test_out_of_distribution.json"
    with open(ood_path, "r", encoding="utf-8") as f:
        ood_data = json.load(f)

    X_ood = [item["prompt"] for item in ood_data]
    y_ood = [int(item["label"]) for item in ood_data]
    X_ood_vec = vectorizer.transform(X_ood)
    y_ood_pred = clf.predict(X_ood_vec)

    ood_acc = accuracy_score(y_ood, y_ood_pred)
    ood_rec = recall_score(y_ood, y_ood_pred, zero_division=0)
    ood_prec = precision_score(y_ood, y_ood_pred, zero_division=0)
    ood_f1 = f1_score(y_ood, y_ood_pred, zero_division=0)

    print(f"\n[Zero-Shot OOD Test (N={len(y_ood)})]")
    print(f"  • Accuracy:  {ood_acc*100:.2f}%")
    print(f"  • Recall:    {ood_rec*100:.2f}%")
    print(f"  • Precision: {ood_prec*100:.2f}%")
    print(f"  • F1-Score:  {ood_f1:.4f}")

    # 4. Breakdown: Human DAN Jailbreaks (76) vs Synthetic Structural Shifts (174)
    dan_indices = [i for i, item in enumerate(ood_data) if "ChatGPT JailbreakBench" in item.get("source", "")]
    synth_indices = [i for i, item in enumerate(ood_data) if "Synthetic" in item.get("source", "")]

    dan_y_true = [y_ood[i] for i in dan_indices]
    dan_y_pred = [y_ood_pred[i] for i in dan_indices]
    dan_rec = recall_score(dan_y_true, dan_y_pred, zero_division=0) if dan_indices else 0.0

    synth_y_true = [y_ood[i] for i in synth_indices]
    synth_y_pred = [y_ood_pred[i] for i in synth_indices]
    synth_rec = recall_score(synth_y_true, synth_y_pred, zero_division=0) if synth_indices else 0.0

    print(f"\n[OOD Granular Breakdown]")
    print(f"  • Human DAN Jailbreaks Recall (N={len(dan_indices)}): {dan_rec*100:.2f}% ({sum(dan_y_pred)}/{len(dan_indices)})")
    print(f"  • Controlled Structural Shifts Recall (N={len(synth_indices)}): {synth_rec*100:.2f}% ({sum(synth_y_pred)}/{len(synth_indices)})")

    out_payload = {
        "metadata": {
            "model": "TfidfVectorizer(ngram=(1,2), max_features=10000) + LogisticRegression(C=1.0)",
            "git_commit": get_git_commit(),
            "train_dataset_sha256": compute_sha256(train_path),
            "in_dist_dataset_sha256": compute_sha256(in_path),
            "ood_dataset_sha256": compute_sha256(ood_path),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "in_distribution": {
            "sample_count": len(y_in),
            "accuracy": round(float(in_acc), 4),
            "recall": round(float(in_rec), 4),
            "precision": round(float(in_prec), 4),
            "f1_score": round(float(in_f1), 4)
        },
        "out_of_distribution": {
            "sample_count": len(y_ood),
            "accuracy": round(float(ood_acc), 4),
            "recall": round(float(ood_rec), 4),
            "precision": round(float(ood_prec), 4),
            "f1_score": round(float(ood_f1), 4),
            "dan_jailbreaks_recall": round(float(dan_rec), 4),
            "dan_sample_count": len(dan_indices),
            "synthetic_template_recall": round(float(synth_rec), 4),
            "synthetic_sample_count": len(synth_indices)
        }
    }

    out_file = REPORTS_DIR / "table_tfidf_baseline_comparison.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(out_payload, f, indent=2)
    print(f"\nSaved TF-IDF baseline results to {out_file}!\n")

if __name__ == "__main__":
    run_tfidf_baseline()
