import sys
import os
import requests
from pathlib import Path

# Configure stdout for utf-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Add src directory to path
sys.path.append(str(Path(__file__).resolve().parent))
import config

def verify_environment():
    print("=" * 60)
    print(f"  [GuardShield AI] Week 1 Environment Verification")
    print("=" * 60)
    
    # 1. Python Version Check
    print(f"\n[1/4] Python Environment:")
    print(f"  * Version: {sys.version.split()[0]}")
    if sys.version_info >= (3, 9):
        print("  [OK] Python version compatible (>= 3.9)")
    else:
        print("  [WARN] Warning: Python 3.9+ recommended")

    # 2. Package Dependency Checks
    print(f"\n[2/4] Package Imports & ML Core:")
    required_packages = [
        "torch",
        "transformers",
        "datasets",
        "fastapi",
        "uvicorn",
        "requests",
        "pandas",
        "numpy"
    ]
    
    installed_packages = {}
    for pkg in required_packages:
        try:
            mod = __import__(pkg)
            version = getattr(mod, "__version__", "installed")
            installed_packages[pkg] = version
            print(f"  [OK] {pkg:<15} : v{version}")
        except ImportError:
            installed_packages[pkg] = None
            print(f"  [FAIL] {pkg:<15} : NOT INSTALLED")

    # 3. Hardware Acceleration Check (PyTorch CUDA / MPS)
    print(f"\n[3/4] Hardware Acceleration (PyTorch):")
    if installed_packages.get("torch"):
        import torch
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            print(f"  [OK] CUDA GPU Acceleration Available: {device_name}")
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            print("  [OK] Apple Silicon MPS GPU Acceleration Available")
        else:
            print("  [INFO] Running on CPU Mode (Sufficient for DeBERTa inference)")
    else:
        print("  [FAIL] PyTorch not available to check device")

    # 4. Local Ollama LLM Connection Check
    print(f"\n[4/4] Local Ollama LLM Engine Status:")
    ollama_url = config.OLLAMA_BASE_URL
    try:
        res = requests.get(f"{ollama_url}/api/tags", timeout=3)
        if res.status_code == 200:
            models_data = res.json().get("models", [])
            model_names = [m.get("name") for m in models_data]
            print(f"  [OK] Ollama Service Running at {ollama_url}")
            print(f"  * Available Local Models: {model_names if model_names else 'No models pulled yet'}")
        else:
            print(f"  [WARN] Ollama returned status code {res.status_code}")
    except Exception:
        print(f"  [INFO] Ollama server not detected at {ollama_url}")
        print("    (Note: You can start Ollama anytime via 'ollama serve' or download it from ollama.com)")

    print("\n" + "=" * 60)
    print("  Week 1 Setup & Environment Verification Completed!")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    verify_environment()
