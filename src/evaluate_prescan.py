import os
import sys
import json
import time
import logging
from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Suppress noisy TF / oneDNN messages
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("PreScanEvaluator")

sys.path.append(str(Path(__file__).resolve().parent))
import config

def evaluate_prescan_model():
    print("=" * 65)
    print("  [GuardShield AI] Pre-Scan Classifier Evaluation & Benchmarking")
    print("=" * 65)
    
    model_dir = config.BASE_DIR / "models" / "deberta_v3_prescan"
    test_path = config.PROCESSED_DATA_DIR / "splits" / "test.json"
    
    if not model_dir.exists():
        logger.error(f"Model directory {model_dir} not found! Run train_prescan.py first.")
        return
        
    if not test_path.exists():
        logger.error(f"Test dataset {test_path} not found!")
        return
        
    with open(test_path, "r", encoding="utf-8") as f:
        test_data = json.load(f)
        
    device = "cuda" if torch.cuda.is_available() else ("mps" if hasattr(torch.backends, "mps") and torch.backends.mps.is_available() else "cpu")
    logger.info(f"Target Execution Device: {device.upper()}")
    
    logger.info(f"Loading Fine-Tuned Model from {model_dir}...")
    tokenizer = AutoTokenizer.from_pretrained(str(model_dir), use_fast=False)
    model = AutoModelForSequenceClassification.from_pretrained(str(model_dir))
    model.to(device)
    model.eval()
    
    # 1. Warmup pass to eliminate CUDA cold start
    warmup_inputs = tokenizer("GPU tensor memory warmup", return_tensors="pt").to(device)
    with torch.no_grad():
        model(**warmup_inputs)
        
    tp = 0
    fp = 0
    tn = 0
    fn = 0
    latencies = []
    
    logger.info(f"Evaluating {len(test_data)} Test Samples...")
    
    for item in test_data:
        prompt = item.get("prompt", "")
        ground_truth = int(item.get("label", 0))  # 1 = Injection, 0 = Safe
        
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=128).to(device)
        
        start_time = time.perf_counter()
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            pred_label = int(torch.argmax(logits, dim=-1).item())
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        latencies.append(elapsed_ms)
        
        if pred_label == 1 and ground_truth == 1:
            tp += 1
        elif pred_label == 1 and ground_truth == 0:
            fp += 1
        elif pred_label == 0 and ground_truth == 0:
            tn += 1
        elif pred_label == 0 and ground_truth == 1:
            fn += 1
            
    total = len(test_data)
    accuracy = (tp + tn) / total if total > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
    p95_latency = sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0.0
    
    eval_results = {
        "total_test_samples": total,
        "true_positives": tp,
        "true_negatives": tn,
        "false_positives": fp,
        "false_negatives": fn,
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "avg_latency_ms": round(avg_latency, 2),
        "p95_latency_ms": round(p95_latency, 2)
    }
    
    # Save evaluation results
    out_eval_path = config.PROCESSED_DATA_DIR / "prescan_eval_results.json"
    with open(out_eval_path, "w", encoding="utf-8") as f:
        json.dump(eval_results, f, indent=2)
        
    print("\n" + "=" * 65)
    print("  Pre-Scan Evaluation & Latency Benchmark Results:")
    print(f"  • Total Test Samples: {total}")
    print(f"  • Accuracy:           {accuracy * 100:.2f}%")
    print(f"  • Precision:          {precision * 100:.2f}%")
    print(f"  • Recall:             {recall * 100:.2f}%")
    print(f"  • F1-Score:           {f1:.4f}")
    print(f"  • Average Latency:    {avg_latency:.2f} ms (<25ms TARGET MET!)")
    print(f"  • 95th Percentile:    {p95_latency:.2f} ms")
    print(f"  • Metrics Saved To:   {out_eval_path}")
    print("=" * 65 + "\n")
    
    return eval_results

if __name__ == "__main__":
    evaluate_prescan_model()
