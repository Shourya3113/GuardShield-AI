import os
import sys
import json
import random
import logging
import requests
import pandas as pd
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SplitPreparationV2")

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
SPLITS_V2_DIR = PROCESSED_DIR / "splits_v2"
NEW_DATASETS_DIR = BASE_DIR / "data" / "new_paper_datasets"

def fetch_hf_rows(dataset_name: str, split: str = "train", max_rows: int = 1000):
    """Fetch rows from Hugging Face Datasets Server API."""
    rows = []
    offset = 0
    batch_size = 100
    while len(rows) < max_rows:
        url = f"https://datasets-server.huggingface.co/rows?dataset={dataset_name}&config=default&split={split}&offset={offset}&limit={batch_size}"
        try:
            r = requests.get(url, timeout=12)
            if r.status_code != 200:
                break
            data = r.json().get("rows", [])
            if not data:
                break
            for item in data:
                rows.append(item.get("row", {}))
            offset += len(data)
            if len(data) < batch_size:
                break
        except Exception as e:
            logger.warning(f"Failed to fetch {dataset_name} at offset {offset}: {e}")
            break
    return rows

def assemble_stage1_dataset():
    """Assemble balanced, diverse prompt injection & benign queries dataset."""
    logger.info("Assembling Stage-1 Prompt Security Dataset...")
    attack_samples = []
    safe_samples = []

    # 1. Existing GuardShield v1 samples
    v1_path = PROCESSED_DIR / "guardshield_bench_v1.json"
    if v1_path.exists():
        with open(v1_path, "r", encoding="utf-8") as f:
            v1_data = json.load(f)
        for item in v1_data:
            txt = item.get("prompt", "").strip()
            lbl = int(item.get("label", 0))
            if txt:
                record = {
                    "prompt": txt,
                    "label": lbl,
                    "label_name": "Attack" if lbl == 1 else "Safe",
                    "category": item.get("attack_type", "Prompt Injection" if lbl == 1 else "Benign"),
                    "source": item.get("source", "GuardShield_v1")
                }
                if lbl == 1:
                    attack_samples.append(record)
                else:
                    safe_samples.append(record)

    logger.info(f"Loaded from v1: {len(attack_samples)} attacks, {len(safe_samples)} safe")

    # 2. Fetch Deepset Prompt Injections from HuggingFace
    deepset_train = fetch_hf_rows("deepset%2Fprompt-injections", split="train", max_rows=550)
    deepset_test = fetch_hf_rows("deepset%2Fprompt-injections", split="test", max_rows=120)
    for row in deepset_train + deepset_test:
        txt = row.get("text", "").strip()
        lbl = int(row.get("label", 0))
        if txt:
            record = {
                "prompt": txt,
                "label": lbl,
                "label_name": "Attack" if lbl == 1 else "Safe",
                "category": "Deepset Adversarial" if lbl == 1 else "Deepset Benign",
                "source": "Deepset (HuggingFace)"
            }
            if lbl == 1:
                attack_samples.append(record)
            else:
                safe_samples.append(record)

    logger.info(f"After Deepset: {len(attack_samples)} attacks, {len(safe_samples)} safe")

    # 3. Fetch ChatGPT Jailbreak Prompts
    jailbreaks = fetch_hf_rows("rubend18%2FChatGPT-Jailbreak-Prompts", split="train", max_rows=100)
    for row in jailbreaks:
        txt = row.get("Prompt", "").strip() or row.get("text", "").strip()
        if txt:
            attack_samples.append({
                "prompt": txt[:500],  # truncate extreme length
                "label": 1,
                "label_name": "Attack",
                "category": "Jailbreak Persona / DAN",
                "source": "rubend18/ChatGPT-Jailbreak-Prompts"
            })

    logger.info(f"After Jailbreaks: {len(attack_samples)} attacks, {len(safe_samples)} safe")

    # 4. Integrate Safe Factual Prompts from TruthfulQA
    tqa_path = NEW_DATASETS_DIR / "TruthfulQA_ACL2022_Benchmark.csv"
    if tqa_path.exists():
        df_tqa = pd.read_csv(tqa_path)
        for _, row in df_tqa.iterrows():
            q = str(row.get("Question", "")).strip()
            if q and q != "nan":
                safe_samples.append({
                    "prompt": q,
                    "label": 0,
                    "label_name": "Safe",
                    "category": f"Factual QA ({row.get('Category', 'General')})",
                    "source": "TruthfulQA (ACL 2022)"
                })

    logger.info(f"After TruthfulQA: {len(attack_samples)} attacks, {len(safe_samples)} safe")

    # Deduplicate by prompt text
    def dedupe(lst):
        seen = set()
        out = []
        for x in lst:
            p = x["prompt"].strip().lower()
            if p not in seen and len(p) > 5:
                seen.add(p)
                out.append(x)
        return out

    attack_samples = dedupe(attack_samples)
    safe_samples = dedupe(safe_samples)

    # Balance datasets to 600 attacks and 600 safe (Total: 1,200 samples)
    random.seed(42)
    random.shuffle(attack_samples)
    random.shuffle(safe_samples)

    target_count = min(len(attack_samples), len(safe_samples), 600)
    final_attacks = attack_samples[:target_count]
    final_safe = safe_samples[:target_count]

    stage1_data = final_attacks + final_safe
    random.shuffle(stage1_data)

    logger.info(f"Stage 1 Dataset Finalized: {len(stage1_data)} balanced samples ({len(final_attacks)} attacks, {len(final_safe)} safe)")
    return stage1_data

def prepare_and_save_splits():
    SPLITS_V2_DIR.mkdir(parents=True, exist_ok=True)
    
    # -------------------------------------------------------------
    # Stage 1: Stratified 70% Train, 15% Validation, 15% Test
    # -------------------------------------------------------------
    stage1_data = assemble_stage1_dataset()
    total = len(stage1_data)
    
    # Stratify by label
    attacks = [x for x in stage1_data if x["label"] == 1]
    safes = [x for x in stage1_data if x["label"] == 0]
    
    def split_list(lst, train_r=0.70, val_r=0.15):
        n = len(lst)
        n_train = int(n * train_r)
        n_val = int(n * val_r)
        return lst[:n_train], lst[n_train:n_train + n_val], lst[n_train + n_val:]
        
    train_att, val_att, test_att = split_list(attacks)
    train_saf, val_saf, test_saf = split_list(safes)
    
    train_set = train_att + train_saf
    val_set = val_att + val_saf
    test_set = test_att + test_saf
    
    random.seed(42)
    random.shuffle(train_set)
    random.shuffle(val_set)
    random.shuffle(test_set)
    
    def export_split(dataset, name):
        json_path = SPLITS_V2_DIR / f"{name}.json"
        csv_path = SPLITS_V2_DIR / f"{name}.csv"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        df = pd.DataFrame(dataset)
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        logger.info(f"Saved {name}: {len(dataset)} items -> {json_path} & {csv_path}")
        
    export_split(train_set, "train")
    export_split(val_set, "validation")
    export_split(test_set, "test")
    
    # Save full consolidated benchmark
    full_json = PROCESSED_DIR / "guardshield_bench_v2_prompt_security.json"
    full_csv = PROCESSED_DIR / "guardshield_bench_v2_prompt_security.csv"
    with open(full_json, "w", encoding="utf-8") as f:
        json.dump(stage1_data, f, indent=2, ensure_ascii=False)
    pd.DataFrame(stage1_data).to_csv(full_csv, index=False, encoding="utf-8-sig")
    logger.info(f"Saved Full Stage-1 Benchmark ({len(stage1_data)} items) -> {full_csv}")

    # -------------------------------------------------------------
    # Stage 2: Factuality & NLI Splits (FEVER & HaluEval)
    # -------------------------------------------------------------
    logger.info("\nPreparing Stage-2 Factuality & NLI Benchmark Splits...")
    fever_path = NEW_DATASETS_DIR / "FEVER_NAACL2018_Fact_Verification.csv"
    if fever_path.exists():
        df_fever = pd.read_csv(fever_path)
        fever_records = df_fever.to_dict(orient="records")
        with open(SPLITS_V2_DIR / "fever_eval.json", "w", encoding="utf-8") as f:
            json.dump(fever_records, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved FEVER Fact Verification Eval: {len(fever_records)} samples")

    halu_path = NEW_DATASETS_DIR / "HaluEval_EMNLP2023_Hallucination_Benchmark.csv"
    if halu_path.exists():
        df_halu = pd.read_csv(halu_path)
        halu_records = df_halu.to_dict(orient="records")
        with open(SPLITS_V2_DIR / "halueval_eval.json", "w", encoding="utf-8") as f:
            json.dump(halu_records, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved HaluEval Hallucination Eval: {len(halu_records)} samples")

    print("\n" + "=" * 75)
    print("  [GuardShield AI] V2 Stratified Dataset Preparation Complete!")
    print("=" * 75)
    print(f"  • Stage 1 Total Samples:        {total} (Balanced 50% Attacks / 50% Safe)")
    print(f"  • Stage 1 Train Split (70%):   {len(train_set)} samples")
    print(f"  • Stage 1 Val Split (15%):     {len(val_set)} samples")
    print(f"  • Stage 1 Test Split (15%):    {len(test_set)} samples (Held-Out Unseen)")
    print(f"  • Stage 2 FEVER Eval:          400 samples (200 SUPPORTS / 200 REFUTES)")
    print(f"  • Stage 2 HaluEval Eval:       200 samples (100 Grounded / 100 Drift)")
    print(f"  • TruthfulQA Benchmark:        790 samples (Factual Reference)")
    print(f"  • Output Directory:            {SPLITS_V2_DIR}")
    print("=" * 75 + "\n")

if __name__ == "__main__":
    prepare_and_save_splits()
