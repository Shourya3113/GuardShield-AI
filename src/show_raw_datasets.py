import sys
import json
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.append(str(Path(__file__).resolve().parent))
import config

def inspect_raw_datasets():
    print("=" * 70)
    print("  🛡️ GuardShield AI — Raw Benchmark Datasets Inspection")
    print("=" * 70)

    # 1. Inspect Prompt Injections Dataset
    injections_file = config.PROCESSED_DATA_DIR / "prompt_injections.json"
    if injections_file.exists():
        with open(injections_file, "r", encoding="utf-8") as f:
            injections_data = json.load(f)
        
        print(f"\n[1] Pre-Scan Prompt Injection Dataset ({injections_file.name}):")
        print(f"  • Total Records: {len(injections_data)}")
        print(f"  • Data Sources: {set(d.get('source_dataset') for d in injections_data)}")
        print(f"  • Sample Raw Records:")
        
        for idx, sample in enumerate(injections_data[:3], 1):
            print(f"\n  --- Sample {idx} [{sample.get('source_dataset')}] ---")
            print(json.dumps(sample, indent=4))
    else:
        print(f"  ✗ Injections file not found at {injections_file}")

    # 2. Inspect Hallucinations Dataset
    hallucinations_file = config.PROCESSED_DATA_DIR / "hallucinations.json"
    if hallucinations_file.exists():
        with open(hallucinations_file, "r", encoding="utf-8") as f:
            hallucinations_data = json.load(f)
        
        print(f"\n\n[2] Post-Scan Hallucinations & Factuality Dataset ({hallucinations_file.name}):")
        print(f"  • Total Records: {len(hallucinations_data)}")
        print(f"  • Data Sources: {set(d.get('source_dataset') for d in hallucinations_data)}")
        print(f"  • Sample Raw Records:")
        
        for idx, sample in enumerate(hallucinations_data[:2], 1):
            print(f"\n  --- Sample {idx} [{sample.get('source_dataset')}] ---")
            print(json.dumps(sample, indent=4))
    else:
        print(f"  ✗ Hallucinations file not found at {hallucinations_file}")

    print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    inspect_raw_datasets()
