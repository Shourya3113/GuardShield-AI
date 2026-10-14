"""
Study C (paper1/SPEC.md section 2): retrains GuardShield's DeBERTa-v3-small with the shipped two-stage recipe,
for one training arm and seed.

  python paper1/study_c/train_arm.py --arm none          --seed 1
  python paper1/study_c/train_arm.py --arm augment       --seed 1 --ratio 1.0
  python paper1/study_c/train_arm.py --arm canon_augment --seed 1 --ratio 1.0

Recipe (as src/train_prescan_v3.py then scripts/train_stage1_hard_negatives.py): stage 1 fine-tunes
microsoft/deberta-v3-small on splits_v3/train.json for 3 epochs (lr 2e-5); stage 2 continues for 1 epoch
(lr 1e-5) on train.json plus the decontaminated hard-negative and attack-retention suites; both select the
best epoch by validation F1. Arms differ only in the training texts:

  none           the shipped data (retrained per seed, so seed variance is measured for every arm)
  augment        each training example gets, with probability --ratio, one extra copy perturbed by a seen
                 family drawn uniformly, with its own label: attacks and benign prompts alike (benign-twin
                 augmentation). Held-out families are never used.
  canon_augment  augment, then every training text passes through the script-aware canonicalizer, which is
                 also applied at inference.

Only training data are perturbed; evaluation items are never seen. Writes models/study_c/<arm>_r<ratio>_s<seed>/.
"""

import argparse
import json
import random
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import torch
from transformers import (AutoModelForSequenceClassification, AutoTokenizer, DataCollatorWithPadding, Trainer,
                          TrainingArguments, set_seed)

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "scripts"))
from guard_audit.canonicalize import script_aware  # noqa: E402
from guard_audit.perturbations import FAMILIES  # noqa: E402
import train_stage1_hard_negatives as stage1  # noqa: E402

SPLITS_DIR = BASE_DIR / "data" / "processed" / "splits_v3"
SEEN = [f for f, fam in FAMILIES.items() if not fam.held_out and fam.kind in ("char", "wrapper")]
BASE_MODEL = "microsoft/deberta-v3-small"


def augment(rows, ratio, rng, canon):
    out = []
    for r in rows:
        out.append(dict(r))
        if ratio > 0 and rng.random() < ratio:
            fam = rng.choice(SEEN)
            out.append({**r, "prompt": FAMILIES[fam].fn(str(r["prompt"])), "augmented_with": fam})
    if canon:
        out = [{**r, "prompt": script_aware(str(r["prompt"]))} for r in out]
    return out


def train_stage(model, tokenizer, rows, val_rows, out_dir, epochs, lr, seed):
    train_ds = stage1.PromptSecurityDataset(rows, tokenizer)
    val_ds = stage1.PromptSecurityDataset(val_rows, tokenizer)
    cuda = torch.cuda.is_available()
    args = TrainingArguments(
        output_dir=str(out_dir / "checkpoints"), num_train_epochs=epochs, per_device_train_batch_size=16,
        per_device_eval_batch_size=32, learning_rate=lr, warmup_ratio=0.1, weight_decay=0.01, logging_steps=50,
        eval_strategy="epoch", save_strategy="epoch", save_total_limit=1, load_best_model_at_end=True,
        metric_for_best_model="f1", greater_is_better=True, fp16=cuda, use_cpu=not cuda, report_to="none", seed=seed,
        data_seed=seed)
    trainer = Trainer(model=model, args=args, train_dataset=train_ds, eval_dataset=val_ds, processing_class=tokenizer,
                      data_collator=DataCollatorWithPadding(tokenizer=tokenizer), compute_metrics=compute_metrics)
    trainer.train()
    return trainer, trainer.evaluate()


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    tp, fp = np.sum((preds == 1) & (labels == 1)), np.sum((preds == 1) & (labels == 0))
    fn = np.sum((preds == 0) & (labels == 1))
    prec, rec = tp / max(1, tp + fp), tp / max(1, tp + fn)
    return {"accuracy": float(np.mean(preds == labels)), "precision": float(prec), "recall": float(rec),
            "f1": float(2 * prec * rec / max(1e-6, prec + rec))}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--arm", choices=["none", "augment", "canon_augment"], required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--ratio", type=float, default=1.0, help="share of training examples given a perturbed copy")
    p.add_argument("--out-root", default=str(BASE_DIR / "models" / "study_c"))
    args = p.parse_args(argv)
    ratio = 0.0 if args.arm == "none" else args.ratio
    out = Path(args.out_root) / f"{args.arm}_r{ratio:g}_s{args.seed}"
    if (out / "training_summary.json").exists():
        print(f"{out} already trained; skipping")
        return
    set_seed(args.seed)
    rng = random.Random(args.seed)
    canon = args.arm == "canon_augment"

    train = json.loads((SPLITS_DIR / "train.json").read_text(encoding="utf-8"))
    val = json.loads((SPLITS_DIR / "validation.json").read_text(encoding="utf-8"))
    eval_texts = stage1.load_eval_texts()
    benign_kept, _ = stage1.decontaminate(stage1.HARD_NEGATIVES_BENIGN, eval_texts)
    attacks_kept, _ = stage1.decontaminate(stage1.HARD_ATTACKS_RETENTION, eval_texts)
    stage2_base = train + [{"prompt": t, "label": 0} for t in benign_kept] + [{"prompt": t, "label": 1} for t in attacks_kept]
    stage1_rows = augment(train, ratio, rng, canon)
    stage2_rows = augment(stage2_base, ratio, rng, canon)
    val_rows = [{**r, "prompt": script_aware(str(r["prompt"]))} for r in val] if canon else val

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, use_fast=False)
    model = AutoModelForSequenceClassification.from_pretrained(BASE_MODEL, num_labels=2)
    trainer, m1 = train_stage(model, tokenizer, stage1_rows, val_rows, out / "stage1", 3, 2.0e-5, args.seed)
    trainer, m2 = train_stage(trainer.model, tokenizer, stage2_rows, val_rows, out / "stage2", 1, 1.0e-5, args.seed)
    trainer.save_model(str(out))
    tokenizer.save_pretrained(str(out))
    for d in ("stage1", "stage2"):
        shutil.rmtree(out / d, ignore_errors=True)  # intermediate checkpoints
    commit = subprocess.run(["git", "-C", str(BASE_DIR), "describe", "--always", "--dirty"], capture_output=True, text=True).stdout.strip()
    (out / "training_summary.json").write_text(json.dumps({
        "arm": args.arm, "ratio": ratio, "seed": args.seed, "seen_families": SEEN if ratio else [],
        "base_model": BASE_MODEL, "n_stage1": len(stage1_rows), "n_stage2": len(stage2_rows),
        "augmented_examples": sum("augmented_with" in r for r in stage2_rows),
        "validation_stage1": m1, "validation_stage2": m2, "git_commit": commit,
        "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
    }, indent=2), encoding="utf-8")
    print(f"saved {out}: validation F1 {m2.get('eval_f1'):.4f}")


if __name__ == "__main__":
    main()
