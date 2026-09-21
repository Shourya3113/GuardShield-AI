# GuardShield AI - Model Checkpoints & Architecture

This directory tracks architecture configurations, tokenizer settings, and training evaluation summaries for GuardShield AI's dual-stage defense pipelines.

> **Note**: Heavy binary model weight files (`*.safetensors`, `*.pt`, `checkpoints/`) are intentionally excluded from git version control due to file size constraints (>100MB per checkpoint). 

---

## 1. Stage 1: Pre-Scan Prompt Injection & Jailbreak Classifier

- **Backbone Architecture**: `microsoft/deberta-v3-small` (44M parameters, 12 layers, 768 hidden dimension).
- **Classification Head**: Binary sequence classification (`SAFE` vs `INJECTION` / `ATTACK`).
- **Current Version**: `v3` (Trained on 3,253 multi-benchmark prompts from Stanford SPML, Jayavibhav, Deepset, and ChatGPT JailbreakBench).

### Reproducing / Training the Weights:
To train the latest Stage 1 classifier on your local GPU:
```bash
python src/train_prescan_v3.py
```
This fine-tunes the model, records metrics to `models/deberta_v3_prescan_v3/mega_training_summary.json`, and saves the weights locally.

---

## 2. Stage 2: Post-Generation Grounding & Hallucination Verifier

- **Backbone Architecture**: `cross-encoder/nli-deberta-v3-small`.
- **Inference Mode**: Zero-shot cross-encoder Natural Language Inference (Premise: Retrieved Context / Truth Benchmark, Hypothesis: Generated Model Response).
- **Entailment Threshold**: `0.50` (`ENTAILMENT` $\to$ Verified Fact; `CONTRADICTION` / `NEUTRAL` $\to$ Hallucination Flagged).
- **Pretrained Weights**: Loaded automatically from Hugging Face Hub during benchmark evaluation or Colab live execution.
