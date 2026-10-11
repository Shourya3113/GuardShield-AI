import os
import sys
import time
import json
import logging
from pathlib import Path
import numpy as np
import torch

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("MeasurePipelineE2E")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src"))

from prescan_filter import PreScanSecurityFilter
from nli_verifier import WindowedNLIVerifier

REPORTS_DIR = BASE_DIR / "docs" / "01 Reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
RAW_OUTPUT_FILE = REPORTS_DIR / "raw_eval_pipeline_e2e.json"

def measure_real_pipeline_latency(num_samples: int = 100):
    logger.info("Initializing Stage 1 & Stage 2 models for empirical sequential latency measurement...")
    prescan = PreScanSecurityFilter()
    nli = WindowedNLIVerifier(threshold=0.50)
    device = prescan.device
    
    # Load authentic held-out test data
    in_dist_file = BASE_DIR / "data" / "processed" / "splits_v3" / "test_in_distribution.json"
    fever_file = BASE_DIR / "data" / "processed" / "splits_v3" / "fever_eval_400.json"
    
    with open(in_dist_file, "r", encoding="utf-8") as f:
        prompts_data = json.load(f)
    with open(fever_file, "r", encoding="utf-8") as f:
        fever_data = json.load(f)
        
    safe_prompts = [p["prompt"] for p in prompts_data if p["label"] == 0][:num_samples]
    fever_pairs = [(r["premise"], r["claim"]) for r in fever_data][:num_samples]
    
    # Warmup
    logger.info("Warming up GPU on sequential pipeline...")
    for _ in range(5):
        if torch.cuda.is_available(): torch.cuda.synchronize()
        _ = prescan.inspect_prompt("Explain quantum computing in simple terms.")
        _ = nli.verify_claim("Quantum computing uses qubits.", "Quantum computers leverage quantum mechanics.")
        if torch.cuda.is_available(): torch.cuda.synchronize()
        
    logger.info(f"Running {num_samples} real sequential end-to-end measurements on {device.upper()}...")
    measurements = []
    latencies = []
    
    for i in range(num_samples):
        prompt = safe_prompts[i % len(safe_prompts)]
        premise, claim = fever_pairs[i % len(fever_pairs)]
        
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        t0 = time.perf_counter()
        
        # Stage 1: Ingress Pre-Scan Filter
        s1_res = prescan.inspect_prompt(prompt)
        
        # Stage 2: Post-Generation Fact Grounding (on approved queries)
        s2_res = nli.verify_claim(premise, claim) if s1_res["is_safe"] else None
        
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        
        latencies.append(elapsed_ms)
        measurements.append({
            "index": i,
            "prompt": prompt,
            "stage1_decision": s1_res["decision"],
            "stage1_risk_score": s1_res["risk_score"],
            "stage1_latency_ms": s1_res["latency_ms"],
            "premise": premise[:100] + "...",
            "claim": claim,
            "stage2_decision": s2_res["decision"] if s2_res else "SKIPPED_BLOCKED",
            "stage2_latency_ms": s2_res["latency_ms"] if s2_res else 0.0,
            "total_e2e_latency_ms": round(elapsed_ms, 2)
        })
        
    latencies = np.array(latencies)
    p50 = round(float(np.median(latencies)), 2)
    mean_val = round(float(np.mean(latencies)), 2)
    p95 = round(float(np.percentile(latencies, 95)), 2)
    std_val = round(float(np.std(latencies)), 2)
    
    import hashlib
    def compute_sha256(filepath):
        p = Path(filepath)
        if not p.is_file(): return None
        h = hashlib.sha256()
        with open(p, "rb") as f:
            while chunk := f.read(65536): h.update(chunk)
        return h.hexdigest()

    import subprocess
    try:
        git_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(BASE_DIR), stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        git_commit = "unknown"

    summary = {
        "metadata": {
            "experiment": "Real Empirical Sequential End-to-End Pipeline Latency",
            "git_commit": git_commit,
            "weights_sha256": compute_sha256(BASE_DIR / "models" / "deberta_v3_prescan_v3" / "model.safetensors"),
            "sample_count": num_samples,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "device": device.upper(),
            "pipeline": "Stage 1 (PreScan DeBERTa-v3 with sliding window) -> Stage 2 (Windowed NLI Cross-Encoder verify_claim)"
        },
        "metrics": {
            "latency_p50_ms": p50,
            "latency_mean_ms": mean_val,
            "latency_p95_ms": p95,
            "latency_std_ms": std_val
        },
        "predictions": measurements
    }
    
    with open(RAW_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        
    logger.info(f"Saved real empirical E2E measurements -> {RAW_OUTPUT_FILE}")
    print("\n" + "=" * 80)
    print("  GuardShield AI — Real Empirical E2E Sequential Pipeline Latency")
    print("=" * 80)
    print(f"  • Total Sequential Queries Measured: {num_samples}")
    print(f"  • Median (p50) Latency:              {p50:.2f} ms")
    print(f"  • Mean Latency:                      {mean_val:.2f} ms (Std: ±{std_val:.2f} ms)")
    print(f"  • 95th Percentile (p95):             {p95:.2f} ms")
    print(f"  • Compute Device:                    {device.upper()}")
    print("=" * 80 + "\n")
    return summary

if __name__ == "__main__":
    measure_real_pipeline_latency(100)
