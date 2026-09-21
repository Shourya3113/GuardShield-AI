import os
import sys
import json
import logging
from pathlib import Path
import numpy as np
import torch
from torch.utils.data import Dataset
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

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("PreScanTrainerV2")

BASE_DIR = Path(__file__).resolve().parent.parent
SPLITS_DIR = BASE_DIR / "data" / "processed" / "splits_v2"
OUTPUT_MODEL_DIR = BASE_DIR / "models" / "deberta_v3_prescan_v2"

class PromptInjectionDataset(Dataset):
    def __init__(self, json_path: Path, tokenizer, max_length: int = 128):
        with open(json_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)
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
    
    return {
        "accuracy": round(float(acc), 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1": round(float(f1), 4)
    }

def train_prescan_v2():
    print("=" * 75)
    print("  [GuardShield AI] Stage-1 Pre-Scan DeBERTa-v3 Fine-Tuning (V2 Benchmark)")
    print("=" * 75)
    
    model_name = "microsoft/deberta-v3-small"
    train_path = SPLITS_DIR / "train.json"
    val_path = SPLITS_DIR / "validation.json"
    OUTPUT_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Target Compute Device: {device.upper()}")
    if device == "cuda":
        logger.info(f"GPU Hardware: {torch.cuda.get_device_name(0)}")
        
    logger.info(f"Loading Base Pre-trained Model: {model_name}")
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
    except Exception:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
    model.to(device)
    
    logger.info(f"Loading Train Split ({train_path})")
    train_dataset = PromptInjectionDataset(train_path, tokenizer)
    logger.info(f"Loading Validation Split ({val_path})")
    val_dataset = PromptInjectionDataset(val_path, tokenizer)
    
    # 3-Epoch Training Setup
    training_args = TrainingArguments(
        output_dir=str(OUTPUT_MODEL_DIR / "checkpoints"),
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=16,
        learning_rate=2.5e-5,
        warmup_ratio=0.1,
        weight_decay=0.01,
        logging_steps=20,
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=1,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        fp16=(device == "cuda"),
        use_cpu=(device == "cpu"),
        report_to="none"
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        processing_class=tokenizer,
        data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
        compute_metrics=compute_metrics
    )
    
    logger.info("Starting Fine-Tuning Execution across 3 Epochs...")
    train_result = trainer.train()
    
    logger.info(f"Training Complete! Global Steps: {train_result.global_step}, Final Train Loss: {train_result.training_loss:.4f}")
    
    # Evaluate on Validation Split
    logger.info("Evaluating Best Model on Validation Split...")
    eval_metrics = trainer.evaluate()
    print("\n" + "-" * 60)
    print("  Validation Set Metrics:")
    for k, v in eval_metrics.items():
        if not k.startswith("eval_runtime") and not k.startswith("eval_samples_per_second"):
            print(f"    • {k:<25}: {v}")
    print("-" * 60 + "\n")
    
    # Save Final Best Model
    logger.info(f"Saving Fine-Tuned Model Weights & Tokenizer -> {OUTPUT_MODEL_DIR}")
    trainer.save_model(str(OUTPUT_MODEL_DIR))
    tokenizer.save_pretrained(str(OUTPUT_MODEL_DIR))
    
    # Write summary metadata
    meta = {
        "model_architecture": "DeBERTa-v3-small",
        "parameters": "86M",
        "train_samples": len(train_dataset),
        "val_samples": len(val_dataset),
        "epochs": 3,
        "validation_metrics": eval_metrics
    }
    with open(OUTPUT_MODEL_DIR / "training_summary.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
        
    print("=" * 75)
    print(f"  Pre-Scan V2 Model Fine-Tuning Successful!")
    print(f"  Artifacts saved at: {OUTPUT_MODEL_DIR}")
    print("=" * 75 + "\n")

if __name__ == "__main__":
    train_prescan_v2()
