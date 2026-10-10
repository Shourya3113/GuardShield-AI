import os
import sys
import time
import zipfile
import logging
from pathlib import Path

if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("PackageFullProject")

BASE_DIR = Path(__file__).resolve().parent.parent
DOWNLOADS_DIR = Path(os.environ.get("USERPROFILE", os.path.expanduser("~"))) / "Downloads"
OUTPUT_ZIP = DOWNLOADS_DIR / "GuardShield_AI_Full_Project.zip"

EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".vscode",
    "tmp_test",
    "scratch",
    "logs",
    "checkpoints",
}
EXCLUDE_FILES = {
    "optimizer.pt",
    "rng_state.pth",
    "scaler.pt",
    "scheduler.pt",
    "trainer_state.json",
}
EXCLUDE_EXTS = {
    ".pyc",
    ".tmp",
    ".zip",
    ".tar.gz",
}

def create_full_project_zip(output_path: Path = OUTPUT_ZIP) -> Path:
    logger.info(f"Packaging GuardShield AI project from: {BASE_DIR}")
    logger.info(f"Target Zip Archive: {output_path}")
    
    t0 = time.time()
    total_files = 0
    total_uncompressed = 0
    
    # Ensure Downloads directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as zf:
        for root, dirs, files in os.walk(BASE_DIR):
            # Prune excluded directories in-place
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith("checkpoint-")]
            
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if f in EXCLUDE_FILES or ext in EXCLUDE_EXTS:
                    continue
                
                full_path = Path(root) / f
                rel_path = full_path.relative_to(BASE_DIR)
                arc_name = Path("GuardShield-AI") / rel_path
                
                zf.write(full_path, arc_name)
                total_files += 1
                total_uncompressed += full_path.stat().st_size
                
    elapsed = time.time() - t0
    zip_size = output_path.stat().st_size
    
    logger.info(f"Archive successfully created in {elapsed:.2f}s!")
    logger.info(f"  • Files Packaged:      {total_files:,}")
    logger.info(f"  • Uncompressed Size:   {total_uncompressed / (1024**2):.2f} MB ({total_uncompressed / (1024**3):.2f} GB)")
    logger.info(f"  • Compressed Zip Size: {zip_size / (1024**2):.2f} MB ({zip_size / (1024**3):.2f} GB)")
    logger.info(f"  • Compression Ratio:   {(1.0 - zip_size / max(1, total_uncompressed)) * 100:.1f}% space saved")
    logger.info(f"  • Destination Path:    {output_path}")
    
    # Verify archive integrity
    logger.info("Verifying archive integrity with testzip()...")
    with zipfile.ZipFile(output_path, "r") as zf:
        first_bad = zf.testzip()
        if first_bad is not None:
            raise RuntimeError(f"Corrupted file detected in archive: {first_bad}")
    logger.info("Integrity check passed! Archive is 100% verified.")
    return output_path

if __name__ == "__main__":
    create_full_project_zip()
