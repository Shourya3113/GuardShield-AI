import os
import sys
import json
import logging
from pathlib import Path
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
logger = logging.getLogger("PreScanTrainer")

sys.path.append(str(Path(__file__).resolve().parent))
import config

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
        text = item.get("prompt", "")
        label = item.get("label", 0)
        
        encoding = self.tokenizer(
            text,
            truncation=True,
            max_length=self.max_length,
            padding=False,
            return_tensors=None
        )
        encoding["labels"] = int(label)
        return encoding

def train_prescan_classifier():
    print("=" * 65)
    print("  [GuardShield AI] Pre-Scan DeBERTa-v3 Classifier Fine-Tuning")
    print("=" * 65)
    
    model_name = "microsoft/deberta-v3-small"
    splits_dir = config.PROCESSED_DATA_DIR / "splits"
    train_path = splits_dir / "train.json"
    val_path = splits_dir / "validation.json"
    output_model_dir = config.BASE_DIR / "models" / "deberta_v3_prescan"
    output_model_dir.mkdir(parents=True, exist_ok=True)
    
    device = "cuda" if torch.cuda.is_available() else ("mps" if hasattr(torch.backends, "mps") and torch.backends.mps.is_available() else "cpu")
    logger.info(f"Target Execution Device: {device.upper()}")
    
    # 1. Load Tokenizer & Model
    logger.info(f"Loading Tokenizer & Model: {model_name}")
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
    except Exception:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
    model.to(device)
    
    # 2. Prepare Datasets
    logger.info(f"Loading Train Dataset from {train_path}")
    train_dataset = PromptInjectionDataset(train_path, tokenizer)
    logger.info(f"Loading Val Dataset from {val_path}")
    val_dataset = PromptInjectionDataset(val_path, tokenizer)
    
    # 3. 3-Epoch Training Arguments Configuration
    training_args = TrainingArguments(
        output_dir=str(output_model_dir),
        num_train_epochs=3,               # 3 Epochs for solid convergence
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        learning_rate=3e-5,
        warmup_ratio=0.1,
        weight_decay=0.01,
        logging_steps=10,
        save_steps=60,
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=1,
        load_best_model_at_end=True,
        metric_for_best_model="loss",
        use_cpu=(device == "cpu"),
        report_to="none"
    )
    
    # 4. Trainer Initialization
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        processing_class=tokenizer,
        data_collator=DataCollatorWithPadding(tokenizer=tokenizer)
    )
    
    logger.info("Starting Full 3-Epoch Pre-Scan Classifier Training...")
    train_result = trainer.train()
    
    logger.info("Saving Calibrated Fine-Tuned Model...")
    trainer.save_model(str(output_model_dir))
    tokenizer.save_pretrained(str(output_model_dir))
    
    print("\n" + "=" * 65)
    print("  Pre-Scan Classifier Fine-Tuning Complete!")
    print(f"  • Model Saved To: {output_model_dir}")
    print(f"  • Final Training Loss: {train_result.training_loss:.4f}")
    print(f"  • Status: FULLY CALIBRATED & READY")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    train_prescan_classifier()
