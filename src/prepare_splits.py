import sys
import json
import random
import logging
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("DatasetSplitter")

sys.path.append(str(Path(__file__).resolve().parent))
import config

def create_train_val_test_splits(train_ratio: float = 0.8, val_ratio: float = 0.1, seed: int = 42):
    print("=" * 65)
    print("  [GuardShield AI] Dataset Train / Validation / Test Splitting")
    print("=" * 65)
    
    bench_file = config.PROCESSED_DATA_DIR / "guardshield_bench_v1.json"
    if not bench_file.exists():
        logger.error(f"File {bench_file} does not exist!")
        return
        
    with open(bench_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    random.seed(seed)
    random.shuffle(data)
    
    total = len(data)
    train_end = int(total * train_ratio)
    val_end = int(total * (train_ratio + val_ratio))
    
    train_set = data[:train_end]
    val_set = data[train_end:val_end]
    test_set = data[val_end:]
    
    splits_dir = config.PROCESSED_DATA_DIR / "splits"
    splits_dir.mkdir(parents=True, exist_ok=True)
    
    def save_split(records, name):
        out_path = splits_dir / f"{name}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {name} split ({len(records)} items) -> {out_path}")
        
    save_split(train_set, "train")
    save_split(val_set, "validation")
    save_split(test_set, "test")
    
    print("\n" + "=" * 65)
    print("  Dataset Splitting Complete!")
    print(f"  • Total Dataset Size: {total} records")
    print(f"  • Train Set (80%): {len(train_set)} records")
    print(f"  • Validation Set (10%): {len(val_set)} records")
    print(f"  • Test Set (10%): {len(test_set)} records")
    print(f"  • Output Directory: {splits_dir}")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    create_train_val_test_splits()
