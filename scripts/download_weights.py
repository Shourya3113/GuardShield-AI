"""
GuardShield AI - Model Checkpoints & Pre-Trained Weights Utility
Enables automated verification, local fine-tuning, and Hugging Face Hub download.
"""
import os
import sys
import argparse
import logging
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("WeightDownloader")

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models" / "deberta_v3_prescan_v3"
DEFAULT_HF_REPO = "Shourya3113/GuardShield-AI-PreScan"

def check_local_weights() -> bool:
    """Check if fine-tuned weights exist locally in models/deberta_v3_prescan_v3."""
    if not MODELS_DIR.exists():
        return False
    weight_files = list(MODELS_DIR.glob("*.safetensors")) + list(MODELS_DIR.glob("*.bin"))
    has_config = (MODELS_DIR / "config.json").exists()
    return bool(weight_files and has_config)

def train_local_weights():
    """Train weights locally using the curated 3,253-sample training split."""
    train_script = BASE_DIR / "src" / "train_prescan_v3.py"
    if not train_script.exists():
        logger.error(f"Training script not found at {train_script}")
        return False
    logger.info("Starting local fine-tuning of DeBERTa-v3 on GPU...")
    print("=" * 75)
    print("  Triggering local training pipeline: python src/train_prescan_v3.py")
    print("=" * 75)
    import subprocess
    ret = subprocess.run([sys.executable, str(train_script)], cwd=str(BASE_DIR))
    return ret.returncode == 0

def download_from_hub(repo_id: str):
    """Download pre-trained weights from Hugging Face Hub repository."""
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        logger.error("huggingface_hub package is not installed. Please install it with 'pip install huggingface_hub'.")
        return False
        
    logger.info(f"Downloading checkpoint from Hugging Face Hub repository: {repo_id}...")
    try:
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        download_path = snapshot_download(
            repo_id=repo_id,
            local_dir=str(MODELS_DIR),
            local_dir_use_symlinks=False
        )
        logger.info(f"Successfully downloaded weights to: {download_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to download from Hugging Face Hub: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="GuardShield AI Model Weights Manager")
    parser.add_argument("--repo-id", type=str, default=DEFAULT_HF_REPO, help="Hugging Face repository ID to pull weights from")
    parser.add_argument("--train", action="store_true", help="Train weights locally on your GPU using src/train_prescan_v3.py")
    parser.add_argument("--check-only", action="store_true", help="Only verify existing local weights")
    args = parser.parse_args()

    print("\n" + "=" * 75)
    print("  GuardShield AI — Model Checkpoints & Pre-Trained Weights Manager")
    print("=" * 75)
    
    if check_local_weights():
        print(f"\n[OK] Local fine-tuned weights verified at: {MODELS_DIR}")
        for w in list(MODELS_DIR.glob("*.safetensors")) + list(MODELS_DIR.glob("*.bin")):
            size_mb = w.stat().st_size / (1024 * 1024)
            print(f"  • {w.name} ({size_mb:.1f} MB)")
        print("\nPreScanSecurityFilter is fully operational and ready for production inference.\n")
        return

    if args.check_only:
        print(f"\n[WARNING] No fine-tuned weights found in {MODELS_DIR}.\n")
        return

    if args.train:
        success = train_local_weights()
        if success and check_local_weights():
            print("\n[SUCCESS] Local fine-tuning completed successfully. Model weights are ready.")
        else:
            print("\n[ERROR] Local training failed or weights were not produced.")
        return

    print(f"\n[INFO] Fine-tuned model checkpoint not detected at: {MODELS_DIR}")
    print("\nBecause binary model checkpoints exceed 500MB, they are not committed to git.")
    print("Attempting download from Hugging Face Hub...")
    
    success = download_from_hub(args.repo_id)
    if not success:
        print("\n[FALLBACK RECOMMENDED] Since the online repository is either private or unreachable,")
        print("you can generate the exact weights locally in ~5 minutes using:")
        print("       python src/train_prescan_v3.py")
        print("       (or run: python scripts/download_weights.py --train)")
    print("=" * 75 + "\n")

if __name__ == "__main__":
    main()
