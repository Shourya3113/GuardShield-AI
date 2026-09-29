import os
import sys

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

import json
import time
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification

def evaluate_raw_batched():
    model_path = "models/deberta_v3_prescan_v3"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading {model_path} on {device.upper()}...", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=False)
    model = AutoModelForSequenceClassification.from_pretrained(model_path).to(device)
    model.eval()

    splits = [
        ("In-Distribution Test (698)", "data/processed/splits_v3/test_in_distribution.json"),
        ("Out-of-Distribution Test (500)", "data/processed/splits_v3/test_out_of_distribution.json")
    ]

    batch_size = 32

    for split_title, split_file in splits:
        with open(split_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        prompts = [item["prompt"] for item in data]
        y_true = np.array([int(item["label"]) for item in data])
        y_pred = []
        latencies = []
        
        t_start = time.perf_counter()
        
        for i in range(0, len(prompts), batch_size):
            batch_prompts = prompts[i:i + batch_size]
            t0 = time.perf_counter()
            inputs = tokenizer(batch_prompts, return_tensors="pt", truncation=True, max_length=128, padding=True).to(device)
            with torch.no_grad():
                out = model(**inputs)
                probs = torch.softmax(out.logits, dim=-1)[:, 1].cpu().numpy()
            t_batch = (time.perf_counter() - t0) * 1000.0 / len(batch_prompts)
            latencies.extend([t_batch] * len(batch_prompts))
            preds = (probs >= 0.5).astype(int).tolist()
            y_pred.extend(preds)
            
        elapsed_total = time.perf_counter() - t_start
        y_pred = np.array(y_pred)
        
        tp = int(np.sum((y_pred == 1) & (y_true == 1)))
        tn = int(np.sum((y_pred == 0) & (y_true == 0)))
        fp = int(np.sum((y_pred == 1) & (y_true == 0)))
        fn = int(np.sum((y_pred == 0) & (y_true == 1)))
        total = len(y_true)
        
        acc = (tp + tn) / total
        rec = tp / max(1, (tp + fn))
        prec = tp / max(1, (tp + fp))
        f1 = 2 * (prec * rec) / max(1e-6, (prec + rec))
        fpr = fp / max(1, (fp + tn))
        med_lat = float(np.median(latencies))
        
        print("\n" + "=" * 65, flush=True)
        print(f"  PURE UNBOOSTED MODEL EVALUATION: {split_title}", flush=True)
        print("=" * 65, flush=True)
        print(f"Total: {total} | TP: {tp}, TN: {tn}, FP: {fp}, FN: {fn}", flush=True)
        print(f"Accuracy:    {acc*100:.2f}%", flush=True)
        print(f"Precision:   {prec*100:.2f}%", flush=True)
        print(f"Recall:      {rec*100:.2f}%", flush=True)
        print(f"F1-Score:    {f1:.4f}", flush=True)
        print(f"FPR:         {fpr*100:.2f}%", flush=True)
        print(f"Per-sample Lat: {med_lat:.2f} ms", flush=True)
        print(f"Total Time:  {elapsed_total:.2f} s", flush=True)

if __name__ == "__main__":
    evaluate_raw_batched()
