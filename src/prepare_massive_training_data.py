"""
================================================================================
 GuardShield AI — Massive Benchmark Dataset Preparation Pipeline
================================================================================
 Automated ingestion, deduplication, and balancing of open-source research
 datasets for Stage-1 Ingress Security and Stage-2 Egress Hallucination Verification.

 Sources Integrated:
   [Stage 1 Security]:
     • Jayavibhav Prompt Injection (327K corpus)
     • Stanford SPML Chatbot Injections (16K corpus)
     • PKU-Alignment BeaverTails (330K safety corpus)
     • Deepset Prompt Injections (662 samples)
     • LibrAI Do-Not-Answer (936 high-risk attacks)
     • XSTest v2 Benchmark (Exaggerated safety FPR control)
   [Stage 2 Hallucination & Factuality]:
     • FEVER NAACL 2018 (Wikipedia Gold Evidence Claims)
     • HaluEval EMNLP 2023 (Verified Knowledge QA Hallucinations)

 Exports to:
   data/massive_benchmark/
     ├── stage1_train.json / .csv
     ├── stage1_val.json / .csv
     ├── stage1_test_indist.json / .csv
     ├── stage1_test_xstest.json / .csv        (FPR benchmark)
     ├── stage1_test_long_context.json / .csv  (Length ablation benchmark)
     ├── stage2_train.json / .csv
     ├── stage2_val.json / .csv
     ├── stage2_test_fever.json / .csv
     ├── stage2_test_halueval.json / .csv
     └── dataset_manifest.json
================================================================================
"""

import os
import sys
import json
import time
import random
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Suppress HuggingFace hub symlink noise on Windows
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("MassiveDataPipeline")

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUT_DIR = BASE_DIR / "data" / "massive_benchmark"

def deduplicate_records(records: List[Dict[str, Any]], text_key: str = "prompt") -> List[Dict[str, Any]]:
    """Remove exact duplicates and whitespace/case variations."""
    seen = set()
    cleaned = []
    for r in records:
        txt = str(r.get(text_key, "")).strip().lower()
        if len(txt) >= 8 and txt not in seen:
            seen.add(txt)
            cleaned.append(r)
    return cleaned

def fetch_stage1_security_data(target_samples: int = 20000) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Stream and curate Stage-1 Ingress Security samples:
      Returns (in_dist_samples, xstest_samples, long_context_samples).
    """
    from datasets import load_dataset

    logger.info("=" * 80)
    logger.info(f"  [STAGE 1] Streaming Massive Security Datasets (Target: {target_samples} Balanced Samples)")
    logger.info("=" * 80)

    attacks: List[Dict[str, Any]] = []
    safes: List[Dict[str, Any]] = []
    xstest_samples: List[Dict[str, Any]] = []

    target_per_class = target_samples // 2

    # 1. Jayavibhav Prompt Injection (Attack & Safe)
    logger.info("[1/6] Ingesting Jayavibhav Prompt Injection Corpus (327K Available)...")
    try:
        ds = load_dataset("jayavibhav/prompt-injection", split="train", streaming=True)
        count_atk, count_safe = 0, 0
        limit = int(target_per_class * 0.45)
        for item in ds:
            txt = str(item.get("text", "")).strip()
            lbl = int(item.get("label", 0))
            if len(txt) > 8:
                rec = {
                    "prompt": txt,
                    "label": lbl,
                    "label_name": "Attack" if lbl == 1 else "Safe",
                    "source": "jayavibhav/prompt-injection",
                    "category": "Direct Prompt Injection" if lbl == 1 else "Standard Query"
                }
                if lbl == 1 and count_atk < limit:
                    attacks.append(rec)
                    count_atk += 1
                elif lbl == 0 and count_safe < limit:
                    safes.append(rec)
                    count_safe += 1
            if count_atk >= limit and count_safe >= limit:
                break
        logger.info(f"  -> Extracted: {count_atk} attacks, {count_safe} safe queries.")
    except Exception as e:
        logger.warning(f"  -> Warning streaming Jayavibhav dataset: {e}")

    # 2. Stanford SPML Chatbot Injections
    logger.info("[2/6] Ingesting Stanford SPML Chatbot Injections (16K Available)...")
    try:
        ds = load_dataset("reshabhs/SPML_Chatbot_Prompt_Injection", split="train", streaming=True)
        count_atk, count_safe = 0, 0
        limit = int(target_per_class * 0.25)
        for item in ds:
            txt = str(item.get("User Prompt", "")).strip()
            lbl = int(item.get("Prompt injection", 0))
            if len(txt) > 8:
                rec = {
                    "prompt": txt,
                    "label": lbl,
                    "label_name": "Attack" if lbl == 1 else "Safe",
                    "source": "Stanford SPML (16K)",
                    "category": "Chatbot Jailbreak" if lbl == 1 else "Conversational Safe"
                }
                if lbl == 1 and count_atk < limit:
                    attacks.append(rec)
                    count_atk += 1
                elif lbl == 0 and count_safe < limit:
                    safes.append(rec)
                    count_safe += 1
            if count_atk >= limit and count_safe >= limit:
                break
        logger.info(f"  -> Extracted: {count_atk} attacks, {count_safe} safe queries.")
    except Exception as e:
        logger.warning(f"  -> Warning streaming Stanford SPML dataset: {e}")

    # 3. PKU-Alignment BeaverTails (Safety and Harms)
    logger.info("[3/6] Ingesting PKU-Alignment BeaverTails Dataset (330K Available)...")
    try:
        ds = load_dataset("PKU-Alignment/BeaverTails", split="30k_train", streaming=True)
        count_atk, count_safe = 0, 0
        limit = int(target_per_class * 0.25)
        for item in ds:
            txt = str(item.get("prompt", "")).strip()
            is_safe = bool(item.get("is_safe", True))
            lbl = 0 if is_safe else 1
            cat = str(item.get("category", "General Safety"))
            if len(txt) > 8:
                rec = {
                    "prompt": txt,
                    "label": lbl,
                    "label_name": "Attack" if lbl == 1 else "Safe",
                    "source": "PKU-Alignment BeaverTails",
                    "category": f"Harmful Query ({cat})" if lbl == 1 else "Safe Dialogue"
                }
                if lbl == 1 and count_atk < limit:
                    attacks.append(rec)
                    count_atk += 1
                elif lbl == 0 and count_safe < limit:
                    safes.append(rec)
                    count_safe += 1
            if count_atk >= limit and count_safe >= limit:
                break
        logger.info(f"  -> Extracted: {count_atk} attacks, {count_safe} safe queries.")
    except Exception as e:
        logger.warning(f"  -> Warning streaming BeaverTails dataset: {e}")

    # 4. Deepset Prompt Injections
    logger.info("[4/6] Ingesting Deepset Prompt Injections...")
    try:
        ds = load_dataset("deepset/prompt-injections", split="train", streaming=True)
        count_atk, count_safe = 0, 0
        for item in ds:
            txt = str(item.get("text", "")).strip()
            lbl = int(item.get("label", 0))
            if len(txt) > 8:
                rec = {
                    "prompt": txt,
                    "label": lbl,
                    "label_name": "Attack" if lbl == 1 else "Safe",
                    "source": "deepset/prompt-injections",
                    "category": "Direct Injection" if lbl == 1 else "Benign Code/Query"
                }
                if lbl == 1:
                    attacks.append(rec)
                    count_atk += 1
                else:
                    safes.append(rec)
                    count_safe += 1
        logger.info(f"  -> Extracted: {count_atk} attacks, {count_safe} safe queries.")
    except Exception as e:
        logger.warning(f"  -> Warning streaming Deepset dataset: {e}")

    # 5. LibrAI Do-Not-Answer (Targeted High-Risk Attacks)
    logger.info("[5/6] Ingesting LibrAI Do-Not-Answer Benchmark...")
    try:
        ds = load_dataset("LibrAI/do-not-answer", split="train", streaming=True)
        count = 0
        for item in ds:
            txt = str(item.get("question", "")).strip()
            harm = str(item.get("types_of_harm", "Policy Violation"))
            if len(txt) > 10:
                attacks.append({
                    "prompt": txt,
                    "label": 1,
                    "label_name": "Attack",
                    "source": "LibrAI/do-not-answer",
                    "category": f"Malicious Adversarial ({harm})"
                })
                count += 1
        logger.info(f"  -> Extracted: {count} adversarial attacks.")
    except Exception as e:
        logger.warning(f"  -> Warning streaming do-not-answer dataset: {e}")

    # 6. XSTest v2 Benchmark (Dedicated Exaggerated Safety FPR Split)
    logger.info("[6/6] Ingesting XSTest v2 Exaggerated-Safety Benchmark (natolambert/xstest-v2-copy)...")
    try:
        ds = load_dataset("natolambert/xstest-v2-copy", split="prompts", streaming=True)
        count_xstest = 0
        for item in ds:
            txt = str(item.get("prompt", "")).strip()
            typ = str(item.get("type", "contrast"))
            if len(txt) > 5:
                xstest_samples.append({
                    "prompt": txt,
                    "label": 0,  # XSTest prompts are predominantly benign prompts designed to trigger false refusals
                    "label_name": "Safe (Exaggerated Safety Trigger)",
                    "source": "XSTest v2 Benchmark",
                    "category": f"Exaggerated Safety ({typ})"
                })
                count_xstest += 1
        logger.info(f"  -> Extracted: {count_xstest} XSTest benign evaluation prompts.")
    except Exception as e:
        logger.warning(f"  -> Warning streaming XSTest dataset: {e}")

    # Deduplicate
    attacks = deduplicate_records(attacks, "prompt")
    safes = deduplicate_records(safes, "prompt")
    xstest_samples = deduplicate_records(xstest_samples, "prompt")

    logger.info(f"Pre-Balance Counts -> Attacks: {len(attacks)}, Safe: {len(safes)}, XSTest: {len(xstest_samples)}")

    # Balance attacks and safe
    n_pairs = min(len(attacks), len(safes), target_per_class)
    random.seed(42)
    random.shuffle(attacks)
    random.shuffle(safes)

    final_attacks = attacks[:n_pairs]
    final_safes = safes[:n_pairs]

    in_dist = final_attacks + final_safes
    random.shuffle(in_dist)

    # Extract long-context ablation candidates (prompts > 100 words / ~130 tokens)
    long_context_samples = [
        item for item in in_dist if len(item["prompt"].split()) >= 60
    ][:500]

    logger.info(f"Final Stage 1 Balanced Set: {len(in_dist)} samples ({n_pairs} Attack, {n_pairs} Safe)")
    logger.info(f"Final Long-Context Test Split: {len(long_context_samples)} samples")

    return in_dist, xstest_samples, long_context_samples

def fetch_stage2_hallucination_data(target_samples: int = 10000) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Stream and curate Stage-2 Egress Hallucination Verification samples:
      Returns (train_val_samples, fever_test_samples, halueval_test_samples).
    """
    from datasets import load_dataset

    logger.info("=" * 80)
    logger.info(f"  [STAGE 2] Streaming Massive Factuality Datasets (Target: {target_samples} Balanced Samples)")
    logger.info("=" * 80)

    fever_pairs: List[Dict[str, Any]] = []
    halueval_pairs: List[Dict[str, Any]] = []

    target_per_source = target_samples // 2

    # 1. FEVER (Fact Extraction and VERification - Wikipedia Gold Evidence)
    logger.info("[1/2] Ingesting FEVER Wikipedia Benchmark (copenlu/fever_gold_evidence)...")
    try:
        ds = load_dataset("copenlu/fever_gold_evidence", split="train", streaming=True)
        count_sup, count_ref = 0, 0
        limit_half = target_per_source // 2
        for item in ds:
            claim = str(item.get("claim", "")).strip()
            lbl_raw = str(item.get("label", "")).strip().upper()
            evidence = str(item.get("evidence", "")).strip()

            if len(claim) > 10 and len(evidence) > 10:
                if lbl_raw == "SUPPORTS" and count_sup < limit_half:
                    fever_pairs.append({
                        "premise": evidence,
                        "claim": claim,
                        "label": 0,  # 0 = Grounded / Factual Entailment
                        "label_name": "Supported / Grounded",
                        "source": "FEVER (Gold Evidence)",
                        "domain": "Wikipedia Encyclopedia"
                    })
                    count_sup += 1
                elif lbl_raw == "REFUTES" and count_ref < limit_half:
                    fever_pairs.append({
                        "premise": evidence,
                        "claim": claim,
                        "label": 1,  # 1 = Hallucination / Contradiction
                        "label_name": "Refuted / Hallucination",
                        "source": "FEVER (Gold Evidence)",
                        "domain": "Wikipedia Encyclopedia"
                    })
                    count_ref += 1

            if count_sup >= limit_half and count_ref >= limit_half:
                break
        logger.info(f"  -> Extracted: {count_sup} Supported claims, {count_ref} Refuted claims.")
    except Exception as e:
        logger.warning(f"  -> Warning streaming FEVER dataset: {e}")

    # 2. HaluEval (EMNLP 2023 - Verified Knowledge QA Hallucinations)
    logger.info("[2/2] Ingesting HaluEval QA Benchmark (pminervini/HaluEval [qa])...")
    try:
        ds = load_dataset("pminervini/HaluEval", "qa", split="data", streaming=True)
        count_halu = 0
        limit_pairs = target_per_source // 2
        for item in ds:
            knowledge = str(item.get("knowledge", "")).strip()
            question = str(item.get("question", "")).strip()
            right_ans = str(item.get("right_answer", "")).strip()
            hallu_ans = str(item.get("hallucinated_answer", "")).strip()

            premise = f"{knowledge} (Question: {question})"
            if len(knowledge) > 15 and len(right_ans) > 3 and len(hallu_ans) > 3:
                # Add Grounded pair
                halueval_pairs.append({
                    "premise": premise,
                    "claim": right_ans,
                    "label": 0,
                    "label_name": "Grounded / Supported",
                    "source": "HaluEval (EMNLP 2023)",
                    "domain": "Multi-hop QA"
                })
                # Add Hallucinated pair
                halueval_pairs.append({
                    "premise": premise,
                    "claim": hallu_ans,
                    "label": 1,
                    "label_name": "Hallucinated / Contradiction",
                    "source": "HaluEval (EMNLP 2023)",
                    "domain": "Multi-hop QA"
                })
                count_halu += 1

            if count_halu >= limit_pairs:
                break
        logger.info(f"  -> Extracted: {count_halu * 2} HaluEval pairs ({count_halu} Grounded, {count_halu} Hallucinated).")
    except Exception as e:
        logger.warning(f"  -> Warning streaming HaluEval dataset: {e}")

    # Separate dedicated holdout benchmark splits for research paper tables
    random.seed(42)
    random.shuffle(fever_pairs)
    random.shuffle(halueval_pairs)

    # Adaptive holdout split: 20% or max 1,000 pairs for camera-ready paper evaluation
    n_test_fever = min(1000, max(50, int(len(fever_pairs) * 0.20))) if len(fever_pairs) > 50 else len(fever_pairs) // 2
    n_test_halu = min(1000, max(50, int(len(halueval_pairs) * 0.20))) if len(halueval_pairs) > 50 else len(halueval_pairs) // 2

    test_fever = fever_pairs[:n_test_fever]
    train_fever = fever_pairs[n_test_fever:]

    test_halueval = halueval_pairs[:n_test_halu]
    train_halueval = halueval_pairs[n_test_halu:]

    train_val_s2 = train_fever + train_halueval
    random.shuffle(train_val_s2)

    logger.info(f"Final Stage 2 Training/Val Set: {len(train_val_s2)} pairs")
    logger.info(f"Dedicated Paper Evaluation Split (FEVER):    {len(test_fever)} pairs")
    logger.info(f"Dedicated Paper Evaluation Split (HaluEval): {len(test_halueval)} pairs")

    return train_val_s2, test_fever, test_halueval

def save_splits(records: List[Dict[str, Any]], out_dir: Path, base_name: str):
    """Save records in both JSON and CSV formats."""
    import pandas as pd
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"{base_name}.json"
    csv_path = out_dir / f"{base_name}.csv"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    df = pd.DataFrame(records)
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    logger.info(f"  💾 Exported {base_name}: {len(records):>6} rows -> {json_path.name}")

def main():
    parser = argparse.ArgumentParser(description="GuardShield AI Massive Dataset Ingestion Pipeline")
    parser.add_argument("--stage", type=str, choices=["1", "2", "all"], default="all", help="Pipeline stage to prepare")
    parser.add_argument("--stage1-samples", type=int, default=20000, help="Target balanced sample count for Stage 1")
    parser.add_argument("--stage2-samples", type=int, default=10000, help="Target balanced sample count for Stage 2")
    parser.add_argument("--out-dir", type=str, default=str(DEFAULT_OUT_DIR), help="Output directory path")
    args = parser.parse_args()

    out_path = Path(args.out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("  [GuardShield AI] Preparing Massive Datasets for 20GB & 47GB VRAM Training")
    print(f"  Output Directory: {out_path}")
    print("=" * 80)

    manifest: Dict[str, Any] = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "stage1": {},
        "stage2": {}
    }

    # -------------------------------------------------------------
    # STAGE 1 PREPARATION
    # -------------------------------------------------------------
    if args.stage in ["1", "all"]:
        s1_data, s1_xstest, s1_long = fetch_stage1_security_data(target_samples=args.stage1_samples)
        
        # 75% Train, 15% Val, 10% In-Dist Test
        n = len(s1_data)
        n_tr = int(n * 0.75)
        n_vl = int(n * 0.15)
        
        s1_train = s1_data[:n_tr]
        s1_val = s1_data[n_tr:n_tr + n_vl]
        s1_test = s1_data[n_tr + n_vl:]

        print("\n[Exporting Stage 1 Security Splits]")
        save_splits(s1_train, out_path, "stage1_train")
        save_splits(s1_val, out_path, "stage1_val")
        save_splits(s1_test, out_path, "stage1_test_indist")
        save_splits(s1_xstest, out_path, "stage1_test_xstest")
        save_splits(s1_long, out_path, "stage1_test_long_context")

        manifest["stage1"] = {
            "train_count": len(s1_train),
            "val_count": len(s1_val),
            "test_indist_count": len(s1_test),
            "xstest_fpr_count": len(s1_xstest),
            "long_context_count": len(s1_long),
            "total_samples": len(s1_data) + len(s1_xstest)
        }

    # -------------------------------------------------------------
    # STAGE 2 PREPARATION
    # -------------------------------------------------------------
    if args.stage in ["2", "all"]:
        s2_train_val, s2_test_fever, s2_test_halueval = fetch_stage2_hallucination_data(target_samples=args.stage2_samples)
        
        # 85% Train, 15% Val
        n2 = len(s2_train_val)
        n2_tr = int(n2 * 0.85)
        s2_train = s2_train_val[:n2_tr]
        s2_val = s2_train_val[n2_tr:]

        print("\n[Exporting Stage 2 Hallucination Splits]")
        save_splits(s2_train, out_path, "stage2_train")
        save_splits(s2_val, out_path, "stage2_val")
        save_splits(s2_test_fever, out_path, "stage2_test_fever")
        save_splits(s2_test_halueval, out_path, "stage2_test_halueval")

        manifest["stage2"] = {
            "train_count": len(s2_train),
            "val_count": len(s2_val),
            "test_fever_count": len(s2_test_fever),
            "test_halueval_count": len(s2_test_halueval),
            "total_pairs": len(s2_train_val) + len(s2_test_fever) + len(s2_test_halueval)
        }

    # Save Manifest
    manifest_file = out_path / "dataset_manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print("\n" + "=" * 80)
    print(f"  🎉 Massive Dataset Assembly Completed Successfully!")
    print(f"  Dataset Manifest saved: {manifest_file}")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
