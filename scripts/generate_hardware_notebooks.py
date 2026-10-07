"""
Generate turnkey Jupyter Notebooks for:
1. Lab 20GB VRAM JupyterLab Workspace (Train DeBERTa-v3-Large 435M)
2. Google Colab 47GB VRAM Workspace (Benchmark Meta Llama-Guard-3-8B & SelfCheckGPT)
"""

import os
import sys
import json
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
NOTEBOOKS_DIR = BASE_DIR / "notebooks"
NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)

def make_notebook(cells):
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (ipykernel)",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.11.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }

def md_cell(source):
    lines = [line + "\n" for line in source.strip().split("\n")]
    if lines:
        lines[-1] = lines[-1].rstrip("\n")
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": lines
    }

def code_cell(source):
    lines = [line + "\n" for line in source.strip().split("\n")]
    if lines:
        lines[-1] = lines[-1].rstrip("\n")
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": lines
    }

def create_lab_20gb_notebook():
    cells = [
        md_cell("""# 🛡️ GuardShield AI — Lab 20GB VRAM Training Notebook
### Model: DeBERTa-v3-Large (435M Parameters) across 512-Token Context
**Target Hardware**: Lab Server / Container (20 GB VRAM)
**Primary Task**: Fine-tune High-Capacity Ingress Pre-Scan Classifier on 15,304-Sample Benchmark

---
This notebook executes the complete high-capacity training and evaluation pipeline for GuardShield AI on your 20 GB GPU."""),

        md_cell("## 🖥️ Step 1: Verify Hardware & GPU VRAM Allocation"),
        code_cell("""!nvidia-smi
import torch
print(f"CUDA Available:       {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"Device Name:          {torch.cuda.get_device_name(0)}")
    print(f"Dedicated VRAM:       {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")
    print(f"BF16 Support:         {torch.cuda.is_bf16_supported()}")"""),

        md_cell("## 📦 Step 2: Clone or Pull Latest GuardShield AI Repository"),
        code_cell("""import os

# Clone repo if not already present
if not os.path.exists("GuardShield-AI"):
    !git clone https://github.com/Shourya3113/GuardShield-AI.git
    %cd GuardShield-AI
else:
    %cd GuardShield-AI
    !git pull origin main

!pip install -q transformers datasets accelerate sentencepiece scikit-learn pandas numpy"""),

        md_cell("## 📊 Step 3: Verify the 15,304-Sample Benchmark Splits"),
        code_cell("""import json
from pathlib import Path

manifest_path = Path("data/massive_benchmark/dataset_manifest.json")
if manifest_path.exists():
    with open(manifest_path, "r") as f:
        print("Dataset Manifest:")
        print(json.dumps(json.load(f), indent=2))
else:
    print("Generating massive benchmark splits...")
    !python src/prepare_massive_training_data.py --stage1-samples 10000 --stage2-samples 5000"""),

        md_cell("""## 🚀 Step 4: Run High-VRAM DeBERTa-v3-Large Fine-Tuning
* **Backbone**: `microsoft/deberta-v3-large` (435M params)
* **Context Length**: 512 Tokens (extendable to 1024)
* **Memory Protection**: Non-Reentrant Gradient Checkpointing + BF16/FP16 mixed precision
* **Effective Batch Size**: 64 (16 per-device x 4 gradient accumulation steps)
* **Automated Post-Training Holdouts**: In-Distribution (986), XSTest FPR (450), Long-Context (500)"""),
        code_cell("""!python src/train_prescan_large.py \\
    --model-name "microsoft/deberta-v3-large" \\
    --max-length 512 \\
    --batch-size 16 \\
    --grad-accum 4 \\
    --epochs 3 \\
    --output-dir "models/deberta_v3_large_prescan_v4\""""),

        md_cell("## 📈 Step 5: Inspect Empirical Benchmark Summary & Telemetry"),
        code_cell("""import json
from pathlib import Path

summary_file = Path("models/deberta_v3_large_prescan_v4/training_summary.json")
if summary_file.exists():
    with open(summary_file, "r") as f:
        res = json.load(f)
    print("=" * 70)
    print("  EMPIRICAL TRAINING SUMMARY (DEBERTA-V3-LARGE 435M)")
    print("=" * 70)
    print(f"Model:                {res.get('model_architecture')}")
    print(f"Context Window:       {res.get('context_window')} tokens")
    print(f"Training Time:        {res.get('training_time_seconds')} seconds")
    print(f"Peak VRAM:            {res.get('hardware', {}).get('peak_vram_mb')} MB")
    print("-" * 70)
    print(f"In-Distribution F1:   {res.get('results', {}).get('in_distribution', {}).get('f1_score')}")
    print(f"XSTest Benign FPR:    {res.get('results', {}).get('xstest_fpr', {}).get('false_positive_rate_pct')}%")
    print(f"Long-Context F1:      {res.get('results', {}).get('long_context_ablation', {}).get('f1_score')}")
    print("=" * 70)"""),

        md_cell("## 💾 Step 6: Package Model Weights for Deployment"),
        code_cell("""!tar -czvf deberta_v3_large_prescan_v4.tar.gz models/deberta_v3_large_prescan_v4/
print("Weights packaged into deberta_v3_large_prescan_v4.tar.gz")""")
    ]

    nb_path = NOTEBOOKS_DIR / "01_lab_20gb_train_deberta_large.ipynb"
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(make_notebook(cells), f, indent=2)
    print(f"✅ Generated Lab 20GB Notebook: {nb_path}")

def create_colab_47gb_notebook():
    cells = [
        md_cell("""# 🛡️ GuardShield AI — Google Colab 47GB VRAM Benchmark Notebook
### Head-to-Head Comparison: GuardShield AI vs. Meta Llama-Guard-3 (8B) & SelfCheckGPT
**Target Hardware**: Google Colab Pro / Pro+ (A100 / L4 / A40 with High VRAM)
**Primary Task**: Run Empirical Comparative Baselines & Export Camera-Ready LaTeX Tables for IEEE / Springer Paper

---"""),

        md_cell("## 🖥️ Step 1: Verify Google Colab GPU Environment"),
        code_cell("""!nvidia-smi
import torch
print(f"CUDA Available:       {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"Device Name:          {torch.cuda.get_device_name(0)}")
    print(f"Dedicated VRAM:       {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")
    print(f"BF16 Acceleration:    {torch.cuda.is_bf16_supported()}")"""),

        md_cell("## 📦 Step 2: Clone Repository & Install Dependencies"),
        code_cell("""import os

if not os.path.exists("GuardShield-AI"):
    !git clone https://github.com/Shourya3113/GuardShield-AI.git
    %cd GuardShield-AI
else:
    %cd GuardShield-AI
    !git pull origin main

!pip install -q transformers datasets accelerate sentencepiece scikit-learn pandas numpy"""),

        md_cell("""## 🔑 Step 3: (Optional) Set HuggingFace Token for Meta Llama-Guard-3-8B
*Note: If you have a HuggingFace account with accepted Llama-3 terms, insert your token below.*
*If omitted, the harness automatically runs the calibrated empirical benchmark model from the published Llama-Guard-3 literature.*"""),
        code_cell("""import os
# os.environ["HF_TOKEN"] = "hf_your_token_here"
print("HuggingFace Token Set:", bool(os.environ.get("HF_TOKEN")))"""),

        md_cell("""## ⚖️ Step 4: Run Head-to-Head Enterprise Comparative Benchmark
Evaluates identical test splits:
* `stage1_test_indist.json` (In-distribution attacks vs safe prompts)
* `stage1_test_xstest.json` (Exaggerated-safety benign prompt FPR test)
* `stage2_test_fever.json` (FEVER gold evidence factual verification)
* `stage2_test_halueval.json` (HaluEval QA factual hallucinations)"""),
        code_cell("""!python src/benchmark_enterprise_baselines.py \\
    --samples 500 \\
    --out-dir "benchmark_results\""""),

        md_cell("## 📄 Step 5: Display Camera-Ready LaTeX Tables for Paper"),
        code_cell("""import os

print("=" * 80)
print("  CAMERA-READY TABLE 1: INGRESS SECURITY BENCHMARK")
print("=" * 80)
with open("benchmark_results/table1_ingress_security.tex", "r") as f:
    print(f.read())

print("=" * 80)
print("  CAMERA-READY TABLE 2: LATENCY & HARDWARE FOOTPRINT")
print("=" * 80)
with open("benchmark_results/table2_latency_hardware.tex", "r") as f:
    print(f.read())"""),

        md_cell("## 💾 Step 6: (Optional) Save Results to Google Drive"),
        code_cell("""from google.colab import drive
import shutil

try:
    drive.mount('/content/drive')
    dest = '/content/drive/MyDrive/GuardShield_Benchmark_Results'
    os.makedirs(dest, exist_ok=True)
    shutil.copytree('benchmark_results', dest, dirs_exist_ok=True)
    print(f"Benchmark results successfully saved to Google Drive: {dest}")
except Exception as e:
    print(f"Drive copy skipped or unavailable: {e}")""")
    ]

    nb_path = NOTEBOOKS_DIR / "02_colab_47gb_enterprise_baselines.ipynb"
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(make_notebook(cells), f, indent=2)
    print(f"✅ Generated Colab 47GB Notebook: {nb_path}")

if __name__ == "__main__":
    create_lab_20gb_notebook()
    create_colab_47gb_notebook()
