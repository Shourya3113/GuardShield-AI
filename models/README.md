# GuardShield AI - Model Checkpoints & Architecture

This directory tracks architecture configurations, tokenizer settings, and training evaluation summaries for GuardShield AI's dual-stage defense pipelines.

> **Note**: Heavy binary model weight files (`*.safetensors`, `*.pt`, `checkpoints/`) are intentionally excluded from git version control due to file size constraints (>100MB per checkpoint). 

---

## 1. Stage 1: Pre-Scan Prompt Injection & Jailbreak Classifier

- **Backbone Architecture**: `microsoft/deberta-v3-small` (44.3M backbone transformer parameters + 98.3M SentencePiece vocabulary embeddings = ~142.6M total parameters, 6 layers, 12 attention heads, 768 hidden dimension).
- **Classification Head**: Binary sequence classification (`SAFE` vs `INJECTION` / `ATTACK`).
- **Current Version**: `v3` (Trained on 3,253 multi-benchmark prompts from Stanford SPML, Jayavibhav, Deepset, and TruthfulQA benign queries; ChatGPT JailbreakBench is held out for zero-shot OOD evaluation).

### Reproducing / Training the Weights:
To train the latest Stage 1 classifier on your local GPU, run both steps in order:
```bash
python src/train_prescan_v3.py
python scripts/train_stage1_hard_negatives.py
```
1. `train_prescan_v3.py` fine-tunes the base model and records metrics to `models/deberta_v3_prescan_v3/mega_training_summary.json`.
2. `train_stage1_hard_negatives.py` runs one extra epoch with hard-negative benign prompts (code, short follow-ups, Hinglish/Hindi, role-play). Candidates that overlap any evaluation set or regression test are removed first; the kept/removed items and validation metrics are written to `hard_negative_training_summary.json`. It refuses to run twice on the same checkpoint.

---

## 2. Stage 2: Post-Generation Grounding & Hallucination Verifier

- **Backbone Architecture**: `cross-encoder/nli-deberta-v3-small`.
- **Inference Mode**: Zero-shot cross-encoder Natural Language Inference (Premise: Retrieved Context / Truth Benchmark, Hypothesis: Generated Model Response).
- **Decision Threshold**: `0.50` (`CONTRADICTION` $\to$ Hallucination Flagged; `ENTAILMENT` $\to$ Verified Fact; otherwise `UNVERIFIED_NEUTRAL`, i.e. insufficient evidence).
- **Long Premises**: Premises that do not fit the 256-token window are split into sentence-aligned windows; a claim is supported if any window entails it.
- **Pretrained Weights**: Loaded automatically from Hugging Face Hub during benchmark evaluation or Colab live execution.
