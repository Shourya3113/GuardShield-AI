"""
GuardShield AI - Model Checkpoints & Pre-Trained Weights Downloader
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models" / "deberta_v3_prescan_v3"

def main():
    print("=" * 70)
    print("  GuardShield AI — Model Checkpoints & Pre-Trained Weights")
    print("=" * 70)
    
    local_weights = list(MODELS_DIR.glob("*.safetensors")) + list(MODELS_DIR.glob("*.bin"))
    if local_weights:
        print(f"\n[OK] Found local fine-tuned weights at: {MODELS_DIR}")
        for w in local_weights:
            print(f"  • {w.name} ({w.stat().st_size / (1024*1024):.1f} MB)")
        print("\nPreScanSecurityFilter is ready to evaluate.")
        return
        
    print(f"\n[INFO] Fine-tuned model checkpoint not detected at: {MODELS_DIR}")
    print("\nBecause binary model checkpoints exceed 500MB, they are not committed to git.")
    print("\nYou can obtain weights via either method:")
    print("1. Train directly on your local GPU (recommended):")
    print("       python src/train_prescan_v3.py")
    print("   This fine-tunes DeBERTa-v3 on 3,253 curated security samples in ~5 minutes.")
    print("\n2. If using Hugging Face Hub, checkpoints can be pulled using:")
    print("       huggingface-cli download <hub-repo-id> --local-dir models/deberta_v3_prescan_v3")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
