import sys
import json
import pandas as pd
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.append(str(Path(__file__).resolve().parent))
import config

def convert_json_to_csv():
    print("=" * 65)
    print("  [GuardShield AI] Exporting Raw Datasets to CSV Format")
    print("=" * 65)

    raw_dir = config.RAW_DATA_DIR
    processed_dir = config.PROCESSED_DATA_DIR

    # 1. Export Pre-Scan Injections to CSV
    proc_inj_file = processed_dir / "prompt_injections.json"
    if proc_inj_file.exists():
        with open(proc_inj_file, "r", encoding="utf-8") as f:
            inj_data = json.load(f)
        df_inj = pd.DataFrame(inj_data)
        out_csv1 = raw_dir / "prompt_injections_raw.csv"
        df_inj.to_csv(out_csv1, index=False, encoding="utf-8")
        print(f"  [OK] Exported {len(df_inj)} prompt injection records -> {out_csv1}")

    # 2. Export Post-Scan Hallucinations to CSV
    proc_hal_file = processed_dir / "hallucinations.json"
    if proc_hal_file.exists():
        with open(proc_hal_file, "r", encoding="utf-8") as f:
            hal_data = json.load(f)
        # Convert list of dicts to flat DataFrame
        flat_hal = []
        for item in hal_data:
            flat_hal.append({
                "question": item.get("question", ""),
                "right_response": item.get("right_response", ""),
                "incorrect_answers": " | ".join(item.get("incorrect_answers", [])) if isinstance(item.get("incorrect_answers"), list) else str(item.get("incorrect_answers", "")),
                "source_dataset": item.get("source_dataset", "TruthfulQA")
            })
        df_hal = pd.DataFrame(flat_hal)
        out_csv2 = raw_dir / "hallucinations_raw.csv"
        df_hal.to_csv(out_csv2, index=False, encoding="utf-8")
        print(f"  [OK] Exported {len(df_hal)} hallucination records -> {out_csv2}")

    print("\n" + "=" * 65)
    print("  CSV Datasets Ready in data/raw/!")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    convert_json_to_csv()
