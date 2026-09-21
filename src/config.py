import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
for path in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, LOGS_DIR]:
    path.mkdir(parents=True, exist_ok=True)

# Project Metadata
PROJECT_NAME = "GuardShield AI"
PROJECT_VERSION = "0.1.0-Week1"
DOMAIN = "Generative AI & AI Safety"

# Local LLM / Ollama Settings
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", "llama3.1:8b")

# Baseline Thresholds
DEFAULT_ENTROPY_THRESHOLD = 2.5  # Shannon entropy threshold for token uncertainty
