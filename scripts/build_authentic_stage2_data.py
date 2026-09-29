import os
import sys
import json
import logging
from pathlib import Path
from datasets import load_dataset
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("AuthenticStage2Builder")

BASE_DIR = Path(__file__).resolve().parent.parent
SPLITS_DIR = BASE_DIR / "data" / "processed" / "splits_v3"
SPLITS_DIR.mkdir(parents=True, exist_ok=True)

def build_authentic_fever():
    logger.info("Extracting authentic FEVER NAACL 2018 gold evidence pairs...")
    ds = load_dataset("copenlu/fever_gold_evidence", split="validation")
    
    supports = []
    refutes = []
    
    for row in ds:
        lbl = row.get("label")
        ev_list = row.get("evidence", [])
        if not ev_list:
            continue
        evidence_text = " ".join([e[2] for e in ev_list if len(e) > 2 and e[2]]).strip()
        claim_text = str(row.get("claim", "")).strip()
        if not evidence_text or not claim_text:
            continue
            
        rec = {
            "id": f"FEVER_{row.get('original_id', len(supports) + len(refutes))}",
            "premise": evidence_text,
            "claim": claim_text,
            "label": 1 if lbl == "REFUTES" else 0,
            "label_name": "Refuted / Falsehood" if lbl == "REFUTES" else "Supported / Fact",
            "source": "FEVER (NAACL 2018)"
        }
        if lbl == "SUPPORTS" and len(supports) < 200:
            supports.append(rec)
        elif lbl == "REFUTES" and len(refutes) < 200:
            refutes.append(rec)
            
        if len(supports) >= 200 and len(refutes) >= 200:
            break
            
    fever_400 = supports + refutes
    logger.info(f"Assembled authentic FEVER 400: {len(supports)} Supports, {len(refutes)} Refutes")
    return fever_400

def build_authentic_halueval():
    logger.info("Extracting authentic HaluEval EMNLP 2023 QA pairs...")
    ds = load_dataset("pminervini/HaluEval", "qa", split="data")
    
    pairs = []
    count = 0
    for row in ds:
        knowledge = str(row.get("knowledge", "")).strip()
        question = str(row.get("question", "")).strip()
        right_ans = str(row.get("right_answer", "")).strip()
        hallu_ans = str(row.get("hallucinated_answer", "")).strip()
        
        if not knowledge or not right_ans or not hallu_ans:
            continue
            
        # Formulate hypotheses as complete declarative statements answering the question
        # Eliminates length and syntactic confounders between extractive entities and full hallucinated sentences
        pairs.append({
            "id": f"HALU_{count}_G",
            "premise": knowledge,
            "claim": f"The answer to the question '{question}' is {right_ans}.",
            "label": 0,
            "label_name": "Supported / Grounded",
            "source": "HaluEval (EMNLP 2023)"
        })
        # Hallucinated response
        pairs.append({
            "id": f"HALU_{count}_H",
            "premise": knowledge,
            "claim": f"The answer to the question '{question}' is {hallu_ans}.",
            "label": 1,
            "label_name": "Hallucination / Contradiction",
            "source": "HaluEval (EMNLP 2023)"
        })
        count += 1
        if count >= 200:
            break
            
    logger.info(f"Assembled authentic HaluEval 400: {count} questions -> 200 Grounded, 200 Hallucinated")
    return pairs

if __name__ == "__main__":
    fever_data = build_authentic_fever()
    halu_data = build_authentic_halueval()
    
    # Export FEVER
    fever_json = SPLITS_DIR / "fever_eval_400.json"
    fever_csv = SPLITS_DIR / "fever_eval_400.csv"
    with open(fever_json, "w", encoding="utf-8") as f:
        json.dump(fever_data, f, indent=2)
    pd.DataFrame(fever_data).to_csv(fever_csv, index=False)
    
    # Export HaluEval
    halu_json = SPLITS_DIR / "halueval_eval_400.json"
    halu_csv = SPLITS_DIR / "halueval_eval_400.csv"
    with open(halu_json, "w", encoding="utf-8") as f:
        json.dump(halu_data, f, indent=2)
    pd.DataFrame(halu_data).to_csv(halu_csv, index=False)
    
    print("\nSaved authentic benchmarks to:")
    print(f"  {fever_json} ({len(fever_data)} rows)")
    print(f"  {halu_json} ({len(halu_data)} rows)")
