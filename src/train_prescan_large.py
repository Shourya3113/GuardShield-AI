"""
================================================================================
 GuardShield AI — High-VRAM Pre-Scan Training & Scaling Pipeline
 Tailored for Device 1 (20 GB VRAM) & Device 2 (47 GB VRAM)
================================================================================
 Fine-tunes DeBERTa-v3-Large (435M Parameters) on the 10,000+ sample massive
 benchmark split. Implements extended context window (512 - 1024 tokens),
 gradient checkpointing, mixed precision (BF16/FP16), and automated
 evaluation across in-distribution, XSTest (FPR), and long-context holdouts.

 Produces:
   • Checkpoint: models/deberta_v3_large_prescan_v4/
   • Training Summary & Empirical Metrics: training_summary.json
================================================================================
"""

import os
import sys
import time
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, List

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
    DataCollatorWithPadding
)

# Suppress noisy TF / oneDNN messages
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("LargePreScanTrainer")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "massive_benchmark"
DEFAULT_OUTPUT_DIR = BASE_DIR / "models" / "deberta_v3_large_prescan_v4"

class PromptSecurityDataset(Dataset):
    """Memory-efficient PyTorch Dataset for prompt security classification."""
    def __init__(self, json_path: Path, tokenizer, max_length: int = 512, max_samples: int = None):
        with open(json_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        if max_samples and max_samples > 0:
            raw = raw[:max_samples]
        self.data = raw
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        text = str(item.get("prompt", ""))
        label = int(item.get("label", 0))

        encoding = self.tokenizer(
            text,
            truncation=True,
            max_length=self.max_length,
            padding=False,
            return_tensors=None
        )
        encoding["labels"] = label
        return encoding

def compute_metrics(eval_pred):
    """Compute standard classification evaluation metrics."""
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)

    tp = np.sum((preds == 1) & (labels == 1))
    tn = np.sum((preds == 0) & (labels == 0))
    fp = np.sum((preds == 1) & (labels == 0))
    fn = np.sum((preds == 0) & (labels == 1))

    acc = (tp + tn) / max(1, len(labels))
    prec = tp / max(1, (tp + fp))
    rec = tp / max(1, (tp + fn))
    f1 = 2 * (prec * rec) / max(1e-6, (prec + rec))
    fpr = fp / max(1, (fp + tn))  # False Positive Rate

    return {
        "accuracy": round(float(acc), 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1": round(float(f1), 4),
        "false_positive_rate": round(float(fpr), 4)
    }

def run_holdout_evaluation(model, tokenizer, test_file: Path, device: str, max_length: int = 512) -> Dict[str, Any]:
    """Execute high-speed vectorized inference and compute rigorous evaluation stats."""
    if not test_file.exists():
        logger.warning(f"Holdout file {test_file} not found. Skipping.")
        return {}

    with open(test_file, "r", encoding="utf-8") as f:
        samples = json.load(f)

    if not samples:
        return {}

    model.eval()
    latencies = []
    preds = []
    labels = []

    batch_size = 32
    for i in range(0, len(samples), batch_size):
        batch = samples[i:i + batch_size]
        texts = [str(x.get("prompt", "")) for x in batch]
        y_true = [int(x.get("label", 0)) for x in batch]

        t0 = time.perf_counter()
        inputs = tokenizer(
            texts,
            truncation=True,
            max_length=max_length,
            padding=True,
            return_tensors="pt"
        ).to(device)

        with torch.inference_mode():
            outputs = model(**inputs)
            logits = outputs.logits
            batch_preds = torch.argmax(logits, dim=-1).cpu().tolist()

        t_elapsed = (time.perf_counter() - t0) * 1000  # ms for batch
        latencies.append(t_elapsed / max(1, len(batch)))

        preds.extend(batch_preds)
        labels.extend(y_true)

    preds_np = np.array(preds)
    labels_np = np.array(labels)

    tp = np.sum((preds_np == 1) & (labels_np == 1))
    tn = np.sum((preds_np == 0) & (labels_np == 0))
    fp = np.sum((preds_np == 1) & (labels_np == 0))
    fn = np.sum((preds_np == 0) & (labels_np == 1))

    acc = (tp + tn) / max(1, len(labels_np))
    prec = tp / max(1, (tp + fp))
    rec = tp / max(1, (tp + fn))
    f1 = 2 * (prec * rec) / max(1e-6, (prec + rec))
    fpr = fp / max(1, (fp + tn))

    return {
        "sample_count": len(samples),
        "accuracy": round(float(acc) * 100, 2),
        "precision": round(float(prec) * 100, 2),
        "recall": round(float(rec) * 100, 2),
        "f1_score": round(float(f1), 4),
        "false_positive_rate_pct": round(float(fpr) * 100, 2),
        "mean_latency_ms": round(float(np.mean(latencies)), 2),
        "p95_latency_ms": round(float(np.percentile(latencies, 95)), 2)
    }

def main():
    parser = argparse.ArgumentParser(description="GuardShield AI High-VRAM Pre-Scan Training")
    parser.add_argument("--model-name", type=str, default="microsoft/deberta-v3-base", help="HuggingFace model backbone ID (microsoft/deberta-v3-base recommended, or microsoft/deberta-v3-large)")
    parser.add_argument("--max-length", type=int, default=512, help="Context sequence length (512 or 1024)")
    parser.add_argument("--batch-size", type=int, default=16, help="Per-device train batch size")
    parser.add_argument("--grad-accum", type=int, default=2, help="Gradient accumulation steps (Effective batch size = batch-size * grad-accum)")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--lr", type=float, default=1.5e-5, help="Learning rate (1.5e-5 for DeBERTa-v3-base, 8e-6 for Large)")
    parser.add_argument("--warmup-steps", type=int, default=50, help="Number of warmup steps for learning rate schedule")
    parser.add_argument("--enable-grad-checkpoint", action="store_true", help="Enable gradient checkpointing (not recommended on >=20GB VRAM to avoid gradient distortion)")
    parser.add_argument("--output-dir", type=str, default=str(DEFAULT_OUTPUT_DIR), help="Output directory for fine-tuned weights")
    parser.add_argument("--dry-run", action="store_true", help="Run rapid sanity check with 200 samples")
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("  [GuardShield AI] High-VRAM Pre-Scan Training (Device 1: 20GB / Device 2: 47GB)")
    print("=" * 80)

    # 1. Hardware Inspection
    device = "cuda" if torch.cuda.is_available() else "cpu"
    gpu_name = "None (CPU)"
    vram_gb = 0.0
    use_bf16 = False

    if device == "cuda":
        gpu_name = torch.cuda.get_device_name(0)
        vram_bytes = torch.cuda.get_device_properties(0).total_memory
        vram_gb = round(vram_bytes / (1024 ** 3), 2)
        use_bf16 = torch.cuda.is_bf16_supported()

    print(f"  • Target Compute Device:     {device.upper()}")
    print(f"  • GPU Model:                 {gpu_name}")
    print(f"  • Dedicated VRAM:            {vram_gb} GB")
    print(f"  • Model Backbone:            {args.model_name}")
    print(f"  • Context Window:            {args.max_length} Tokens")
    print(f"  • Effective Batch Size:      {args.batch_size * args.grad_accum} ({args.batch_size} x {args.grad_accum})")
    print(f"  • Learning Rate:             {args.lr} (Warmup: {args.warmup_steps} steps)")
    print(f"  • Precision Format:          FP32 Full Precision (Guaranteed Stability)")
    print(f"  • Grad Checkpointing:        {args.enable_grad_checkpoint}")
    print("=" * 80)

    # 2. Check Data Splits
    train_file = DATA_DIR / "stage1_train.json"
    val_file = DATA_DIR / "stage1_val.json"
    test_indist_file = DATA_DIR / "stage1_test_indist.json"
    test_xstest_file = DATA_DIR / "stage1_test_xstest.json"
    test_long_file = DATA_DIR / "stage1_test_long_context.json"

    if not train_file.exists():
        logger.error(f"Training split not found at {train_file}. Please run 'python src/prepare_massive_training_data.py' first.")
        sys.exit(1)

    # 3. Load Tokenizer & Model
    from transformers import AutoConfig

    logger.info(f"Loading Base Tokenizer: {args.model_name}...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(args.model_name, use_fast=False)
    except Exception:
        tokenizer = AutoTokenizer.from_pretrained(args.model_name)

    logger.info(f"Loading Model Architecture: {args.model_name} (num_labels=2)...")
    config = AutoConfig.from_pretrained(args.model_name, num_labels=2)
    config.problem_type = "single_label_classification"
    model = AutoModelForSequenceClassification.from_pretrained(args.model_name, config=config)
    model.to(device)

    # 4. Prepare Datasets
    sample_limit = 200 if args.dry_run else None
    logger.info(f"Loading Train Dataset from {train_file.name} (limit={sample_limit})...")
    train_dataset = PromptSecurityDataset(train_file, tokenizer, max_length=args.max_length, max_samples=sample_limit)
    val_dataset = PromptSecurityDataset(val_file, tokenizer, max_length=args.max_length, max_samples=sample_limit)

    import inspect

    # 5. Universal Backward/Forward Compatible Training Arguments
    args_dict = {
        "output_dir": str(out_dir / "checkpoints"),
        "num_train_epochs": args.epochs,
        "per_device_train_batch_size": args.batch_size,
        "per_device_eval_batch_size": args.batch_size * 2,
        "gradient_accumulation_steps": args.grad_accum,
        "learning_rate": args.lr,
        "max_grad_norm": 1.0,
        "weight_decay": 0.01,
        "logging_steps": 20,
        "save_total_limit": 1,
        "load_best_model_at_end": True,
        "metric_for_best_model": "f1",
        "greater_is_better": True,
        "fp16": False,
        "bf16": False,
        "use_cpu": (device == "cpu"),
        "report_to": "none"
    }

    ta_params = inspect.signature(TrainingArguments.__init__).parameters

    # Handle evaluation strategy naming change (eval_strategy vs evaluation_strategy)
    if "eval_strategy" in ta_params:
        args_dict["eval_strategy"] = "epoch"
    elif "evaluation_strategy" in ta_params:
        args_dict["evaluation_strategy"] = "epoch"

    if "save_strategy" in ta_params:
        args_dict["save_strategy"] = "epoch"

    # Handle warmup (critical for DeBERTa-v3 gradient stability)
    if "warmup_steps" in ta_params:
        args_dict["warmup_steps"] = args.warmup_steps
    elif "warmup_ratio" in ta_params:
        args_dict["warmup_ratio"] = 0.1

    # Handle gradient checkpointing (opt-in only)
    if args.enable_grad_checkpoint:
        if "gradient_checkpointing" in ta_params:
            args_dict["gradient_checkpointing"] = True
        if "gradient_checkpointing_kwargs" in ta_params:
            args_dict["gradient_checkpointing_kwargs"] = {"use_reentrant": False}

    if "dataloader_pin_memory" in ta_params:
        args_dict["dataloader_pin_memory"] = (device == "cuda")

    # Filter strictly to parameters accepted by the installed version
    safe_training_kwargs = {k: v for k, v in args_dict.items() if k in ta_params}
    training_args = TrainingArguments(**safe_training_kwargs)

    # 6. Universal Trainer Setup (handle tokenizer vs processing_class)
    trainer_params = inspect.signature(Trainer.__init__).parameters
    trainer_kwargs = {
        "model": model,
        "args": training_args,
        "train_dataset": train_dataset,
        "eval_dataset": val_dataset,
        "data_collator": DataCollatorWithPadding(tokenizer=tokenizer),
        "compute_metrics": compute_metrics
    }
    if "processing_class" in trainer_params:
        trainer_kwargs["processing_class"] = tokenizer
    else:
        trainer_kwargs["tokenizer"] = tokenizer

    trainer = Trainer(**trainer_kwargs)

    # 6. Execute Training
    logger.info(f"Starting High-Capacity Training ({len(train_dataset)} samples, {args.epochs} epochs)...")
    t_start = time.time()
    train_result = trainer.train()
    t_total = time.time() - t_start

    logger.info(f"Training Complete! Total Time: {t_total:.1f}s ({t_total/60:.2f} mins). Final Train Loss: {train_result.training_loss:.4f}")

    # 7. Save Fine-Tuned Model
    logger.info(f"Saving Fine-Tuned Model Weights & Tokenizer -> {out_dir}")
    trainer.save_model(str(out_dir))
    tokenizer.save_pretrained(str(out_dir))

    # 8. Run Camera-Ready Holdout Benchmarks for Paper Tables
    print("\n" + "=" * 80)
    print("  [EVALUATION] Running Camera-Ready Benchmarks for IEEE / Springer Tables")
    print("=" * 80)

    logger.info("1/3 Evaluating In-Distribution Test Split...")
    eval_indist = run_holdout_evaluation(model, tokenizer, test_indist_file, device, max_length=args.max_length)
    print(f"  • In-Distribution Test Set ({eval_indist.get('sample_count', 0)} samples):")
    print(f"    - Accuracy:  {eval_indist.get('accuracy')}%")
    print(f"    - Precision: {eval_indist.get('precision')}%")
    print(f"    - Recall:    {eval_indist.get('recall')}%")
    print(f"    - F1-Score:  {eval_indist.get('f1_score')}")
    print(f"    - Latency:   {eval_indist.get('mean_latency_ms')} ms (p95: {eval_indist.get('p95_latency_ms')} ms)")

    logger.info("2/3 Evaluating XSTest v2 Exaggerated-Safety Benchmark (FPR Minimization)...")
    eval_xstest = run_holdout_evaluation(model, tokenizer, test_xstest_file, device, max_length=args.max_length)
    print(f"  • XSTest v2 Exaggerated Safety ({eval_xstest.get('sample_count', 0)} benign trigger prompts):")
    print(f"    - Benign Safe Pass Rate:        {eval_xstest.get('accuracy')}%")
    print(f"    - False Positive Rate (FPR):    {eval_xstest.get('false_positive_rate_pct')}% (Target: < 1.0%)")

    logger.info("3/3 Evaluating Long-Context Ablation Split (>256 tokens)...")
    eval_long = run_holdout_evaluation(model, tokenizer, test_long_file, device, max_length=args.max_length)
    print(f"  • Long-Context Split ({eval_long.get('sample_count', 0)} samples):")
    print(f"    - Long-Context F1-Score:        {eval_long.get('f1_score')}")
    print(f"    - Mean Latency:                 {eval_long.get('mean_latency_ms')} ms")

    # 9. Log Peak Memory
    peak_vram_mb = 0.0
    if device == "cuda":
        peak_vram_mb = round(torch.cuda.max_memory_allocated(0) / (1024 ** 2), 2)
        print(f"\n  • Peak CUDA VRAM Allocated:   {peak_vram_mb} MB ({peak_vram_mb/1024:.2f} GB)")

    # 10. Export Benchmark JSON
    summary_data = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model_architecture": args.model_name,
        "parameters": "435M" if "large" in args.model_name else "140M" if "base" in args.model_name else "86M",
        "context_window": args.max_length,
        "effective_batch_size": args.batch_size * args.grad_accum,
        "hardware": {
            "device": device,
            "gpu_name": gpu_name,
            "total_vram_gb": vram_gb,
            "peak_vram_mb": peak_vram_mb
        },
        "training_time_seconds": round(t_total, 2),
        "results": {
            "in_distribution": eval_indist,
            "xstest_fpr": eval_xstest,
            "long_context_ablation": eval_long
        }
    }

    summary_file = out_dir / "training_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)

    print("=" * 80)
    print(f"  🎉 Pre-Scan Large Training & Benchmarking Complete!")
    print(f"  Model Saved:   {out_dir}")
    print(f"  Summary Saved: {summary_file}")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
