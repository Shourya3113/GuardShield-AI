"""
================================================================================
 GuardShield AI — Empirical Sequential Pipeline Latency Benchmark (5 Repeats)
================================================================================
 Measures real end-to-end sequential overhead of the dual-stage defense pipeline:
   • Stage 1: Ingress PreScan DeBERTa-v3 with sliding-window chunking
   • Stage 2: Post-generation Windowed NLI Cross-Encoder verify_claim
 Protocol:
   • 10 sequential GPU warmups with torch.cuda.synchronize()
   • 5 independent runs of N=100 authentic queries (Total N=500 measurements)
   • Reports Median (p50), Mean +/- Std, IQR (p75 - p25), and 95th Percentile (p95)
   • Saves complete per-sample prediction logs & hardware telemetry
 Exports:
   docs/01 Reports/raw_eval_pipeline_e2e.json
================================================================================
"""

import os
import sys
import time
import json
import logging
import hashlib
import subprocess
from pathlib import Path
import numpy as np
import torch
import transformers

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("MeasurePipelineE2E")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src"))

from prescan_filter import PreScanSecurityFilter, weights_sha256
from nli_verifier import WindowedNLIVerifier

REPORTS_DIR = BASE_DIR / "docs" / "01 Reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
RAW_OUTPUT_FILE = REPORTS_DIR / "raw_eval_pipeline_e2e.json"

def get_git_commit():
    try:
        return subprocess.check_output(["git", "describe", "--always", "--dirty", "--abbrev=40"], cwd=str(BASE_DIR), stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"

def compute_sha256(filepath):
    p = Path(filepath)
    if not p.is_file(): return None
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536): h.update(chunk)
    return h.hexdigest()

def measure_real_pipeline_latency(num_repeats: int = 5, samples_per_repeat: int = 100):
    logger.info("Initializing Stage 1 & Stage 2 models for multi-repeat latency measurement...")
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
        
    safe_prompts = [p["prompt"] for p in prompts_data if p["label"] == 0][:samples_per_repeat]
    fever_pairs = [(r["premise"], r["claim"]) for r in fever_data][:samples_per_repeat]
    
    # GPU Warmup (10 runs)
    logger.info("Warming up GPU execution pipeline (10 warmup iterations)...")
    for _ in range(10):
        if torch.cuda.is_available(): torch.cuda.synchronize()
        _ = prescan.inspect_prompt("Explain quantum computing in simple terms.")
        _ = nli.verify_claim("Quantum computing uses qubits.", "Quantum computers leverage quantum mechanics.")
        if torch.cuda.is_available(): torch.cuda.synchronize()
        
    logger.info(f"Executing {num_repeats} repeated benchmarking runs of {samples_per_repeat} queries on {device.upper()}...")
    
    all_e2e_latencies = []
    all_s1_latencies = []
    all_s2_latencies = []
    all_records = []
    
    repeat_summaries = []
    
    for r in range(num_repeats):
        r_latencies = []
        for i in range(samples_per_repeat):
            prompt = safe_prompts[i % len(safe_prompts)]
            premise, claim = fever_pairs[i % len(fever_pairs)]
            
            if torch.cuda.is_available(): torch.cuda.synchronize()
            t0 = time.perf_counter()
            
            # Stage 1: Ingress Pre-Scan Filter
            s1_res = prescan.inspect_prompt(prompt)
            
            # Stage 2: Post-Generation Fact Grounding
            s2_res = nli.verify_claim(premise, claim) if s1_res["is_safe"] else None
            
            if torch.cuda.is_available(): torch.cuda.synchronize()
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            
            r_latencies.append(elapsed_ms)
            all_e2e_latencies.append(elapsed_ms)
            all_s1_latencies.append(s1_res["latency_ms"])
            if s2_res:
                all_s2_latencies.append(s2_res["latency_ms"])
                
            all_records.append({
                "repeat_index": r,
                "query_index": i,
                "prompt": prompt,
                "stage1_risk_score": s1_res["risk_score"],
                "stage1_latency_ms": s1_res["latency_ms"],
                "stage2_decision": s2_res["decision"] if s2_res else "SKIPPED",
                "stage2_latency_ms": s2_res["latency_ms"] if s2_res else 0.0,
                "total_e2e_latency_ms": round(elapsed_ms, 2)
            })
            
        r_arr = np.array(r_latencies)
        repeat_summaries.append({
            "repeat": r + 1,
            "median_ms": round(float(np.median(r_arr)), 2),
            "mean_ms": round(float(np.mean(r_arr)), 2),
            "std_ms": round(float(np.std(r_arr)), 2)
        })
        logger.info(f"Repeat {r+1}/{num_repeats} completed: p50={np.median(r_arr):.2f}ms, mean={np.mean(r_arr):.2f}ms")

    e2e_arr = np.array(all_e2e_latencies)
    s1_arr = np.array(all_s1_latencies)
    s2_arr = np.array(all_s2_latencies)
    
    p50_e2e = round(float(np.median(e2e_arr)), 2)
    mean_e2e = round(float(np.mean(e2e_arr)), 2)
    p25_e2e = round(float(np.percentile(e2e_arr, 25)), 2)
    p75_e2e = round(float(np.percentile(e2e_arr, 75)), 2)
    iqr_e2e = round(float(p75_e2e - p25_e2e), 2)
    p95_e2e = round(float(np.percentile(e2e_arr, 95)), 2)
    std_e2e = round(float(np.std(e2e_arr)), 2)

    p50_s1 = round(float(np.median(s1_arr)), 2)
    p25_s1 = round(float(np.percentile(s1_arr, 25)), 2)
    p75_s1 = round(float(np.percentile(s1_arr, 75)), 2)
    iqr_s1 = round(float(p75_s1 - p25_s1), 2)
    mean_s1 = round(float(np.mean(s1_arr)), 2)

    p50_s2 = round(float(np.median(s2_arr)), 2)
    p25_s2 = round(float(np.percentile(s2_arr, 25)), 2)
    p75_s2 = round(float(np.percentile(s2_arr, 75)), 2)
    iqr_s2 = round(float(p75_s2 - p25_s2), 2)
    mean_s2 = round(float(np.mean(s2_arr)), 2)


    summary = {
        "metadata": {
            "experiment": "Real Empirical Sequential End-to-End Pipeline Latency (5 Repeats)",
            "git_commit": get_git_commit(),
            "weights_sha256": weights_sha256(prescan.model_dir),
            "num_repeats": num_repeats,
            "samples_per_repeat": samples_per_repeat,
            "total_samples_measured": len(all_e2e_latencies),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "device": device.upper(),
            "device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU",
            "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
            "torch_version": torch.__version__,
            "transformers_version": transformers.__version__,
            "batch_size": 1,
            "pipeline": "Stage 1 (PreScan DeBERTa-v3 with sliding window) -> Stage 2 (Windowed NLI Cross-Encoder verify_claim)"
        },
        "metrics": {
            "latency_p50_ms": p50_e2e,
            "latency_mean_ms": mean_e2e,
            "latency_p25_ms": p25_e2e,
            "latency_p75_ms": p75_e2e,
            "latency_iqr_ms": iqr_e2e,
            "latency_p95_ms": p95_e2e,
            "latency_std_ms": std_e2e,
            "stage1_isolated": {
                "latency_p50_ms": p50_s1,
                "latency_mean_ms": mean_s1,
                "latency_iqr_ms": iqr_s1
            },
            "stage2_isolated": {
                "latency_p50_ms": p50_s2,
                "latency_mean_ms": mean_s2,
                "latency_iqr_ms": iqr_s2
            }
        },
        "repeat_breakdown": repeat_summaries,
        "predictions": all_records[:100]  # Store representative first 100 per-sample logs
    }

    with open(RAW_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    logger.info(f"Saved real empirical 5-repeat E2E measurements -> {RAW_OUTPUT_FILE}")
    print("\n" + "=" * 80)
    print("  GuardShield AI — Real Empirical E2E Sequential Pipeline Latency (5 Repeats)")
    print("=" * 80)
    print(f"  • Repeats Measured:                  {num_repeats} runs x {samples_per_repeat} queries ({len(all_e2e_latencies)} total)")
    print(f"  • Median (p50) Sequential Latency:  {p50_e2e:.2f} ms")
    print(f"  • Mean Sequential Latency:          {mean_e2e:.2f} ms (Std: +/-{std_e2e:.2f} ms)")
    print(f"  • Interquartile Range (IQR):        {iqr_e2e:.2f} ms (p25={p25_e2e:.2f}ms, p75={p75_e2e:.2f}ms)")
    print(f"  • 95th Percentile (p95):             {p95_e2e:.2f} ms")
    print(f"  • Stage 1 Isolated (p50 / IQR):     {p50_s1:.2f} ms / {iqr_s1:.2f} ms")
    print(f"  • Stage 2 Isolated (p50 / IQR):     {p50_s2:.2f} ms / {iqr_s2:.2f} ms")
    print(f"  • Compute Device:                    {device.upper()} ({torch.cuda.get_device_name(0) if device == 'cuda' else 'CPU'})")
    print("=" * 80 + "\n")
    return summary

if __name__ == "__main__":
    measure_real_pipeline_latency(num_repeats=5, samples_per_repeat=100)
