"""
================================================================================
 GuardShield AI — Multi-Turn Benign Dialogue Benchmark Evaluation
================================================================================
 Evaluates both GuardShield AI and ProtectAI DeBERTa-v3 on the 20-conversation,
 100-turn held-out benign dialogue benchmark (data/multiturn_benchmark_eval.json).

 Measures:
   1. Per-Turn False Positive Rate (FPR) across all 100 turns.
   2. Per-Turn False Positive Rate on User Turns only (N=60).
   3. Per-Turn False Positive Rate on Assistant Turns only (N=40).
   4. Per-Conversation False Positive Rate (Compound FPR): percentage of
      conversations that encounter at least one false alarm and get blocked.
   5. GuardShield with Signed History: Relayed assistant turns are verified by
      HMAC signature, preventing compounded false alarms on model's own text.

 Exports:
   docs/01 Reports/table_multiturn_benchmark.json
================================================================================
"""

import os
import sys
import json
import time
import hashlib
import subprocess
from pathlib import Path
import numpy as np
import torch
import transformers
from transformers import AutoTokenizer, AutoModelForSequenceClassification

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src"))

from prescan_filter import PreScanSecurityFilter, weights_sha256
from proxy_server import compute_assistant_signature, scan_messages

DATA_FILE = BASE_DIR / "data" / "multiturn_benchmark_eval.json"
REPORTS_DIR = BASE_DIR / "docs" / "01 Reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = REPORTS_DIR / "table_multiturn_benchmark.json"

PROTECTAI_MODEL_ID = "protectai/deberta-v3-base-prompt-injection-v2"

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

def evaluate_multiturn():
    print("=" * 80)
    print("  GuardShield AI — Multi-Turn Benign Dialogue Evaluation")
    print("=" * 80)

    if not DATA_FILE.is_file():
        raise FileNotFoundError(f"Missing benchmark file: {DATA_FILE}")

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        bench_data = json.load(f)

    conversations = bench_data["conversations"]
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # 1. Initialize GuardShield PreScan Filter
    print(f"\n[1/3] Loading GuardShield Stage 1 PreScan Filter on {device.upper()}...")
    guardshield_engine = PreScanSecurityFilter()

    # 2. Initialize ProtectAI DeBERTa-v3
    print(f"\n[2/3] Loading ProtectAI ({PROTECTAI_MODEL_ID}) on {device.upper()}...")
    try:
        pai_tokenizer = AutoTokenizer.from_pretrained(PROTECTAI_MODEL_ID, local_files_only=True)
        pai_model = AutoModelForSequenceClassification.from_pretrained(PROTECTAI_MODEL_ID, local_files_only=True).to(device)
    except Exception:
        pai_tokenizer = AutoTokenizer.from_pretrained(PROTECTAI_MODEL_ID)
        pai_model = AutoModelForSequenceClassification.from_pretrained(PROTECTAI_MODEL_ID).to(device)
    pai_model.eval()

    def score_protectai(text: str) -> float:
        inputs = pai_tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to(device)
        with torch.no_grad():
            logits = pai_model(**inputs).logits
            probs = torch.softmax(logits, dim=-1)[0]
            return float(probs[1].item())

    # 3. Evaluate across conversations
    # GuardShield is scored with the proxy's own multi-turn logic (proxy_server.scan_messages):
    #   raw    -> no turn is signed, so assistant turns are scanned like any untrusted turn
    #   signed -> every assistant turn carries a valid proxy signature (as when relayed by the proxy)
    print("\n[3/3] Evaluating conversations...")

    gs_all_preds = []
    gs_user_preds = []
    gs_asst_preds = []
    gs_signed_user_preds = []

    gs_signed_conv_blocked = 0
    gs_raw_conv_blocked = 0

    pai_all_preds = []
    pai_user_preds = []
    pai_asst_preds = []
    pai_conv_blocked = 0

    detailed_conv_results = []
    never_signed = lambda content, sig: False

    for c_idx, conv in enumerate(conversations):
        cid = conv["conversation_id"]
        turns = conv["turns"]

        raw_scan = scan_messages(guardshield_engine, turns, verify_signature=never_signed, stop_on_block=False)
        signed_turns = [
            dict(t, proxy_signature=compute_assistant_signature(t["content"])) if t["role"] == "assistant" else t
            for t in turns
        ]
        signed_scan = scan_messages(guardshield_engine, signed_turns, stop_on_block=False)
        raw_by_idx = {r["index"]: r for r in raw_scan["turns"]}
        signed_by_idx = {r["index"]: r for r in signed_scan["turns"]}

        conv_turns_log = []
        c_pai_blocked = False
        for t_idx, turn in enumerate(turns):
            role = turn["role"]
            content = turn["content"]

            gs_raw = raw_by_idx.get(t_idx)
            gs_risk = gs_raw["risk_score"] if gs_raw else 0.0
            gs_pred = 0 if (gs_raw is None or gs_raw["is_safe"]) else 1
            gs_signed = signed_by_idx.get(t_idx)
            gs_signed_pred = 0 if (gs_signed is None or gs_signed["is_safe"]) else 1

            # ProtectAI turn scoring (stateless)
            pai_risk = score_protectai(content)
            pai_pred = 1 if pai_risk >= 0.50 else 0

            gs_all_preds.append(gs_pred)
            pai_all_preds.append(pai_pred)
            if role == "user":
                gs_user_preds.append(gs_pred)
                gs_signed_user_preds.append(gs_signed_pred)
                pai_user_preds.append(pai_pred)
            elif role == "assistant":
                gs_asst_preds.append(gs_pred)
                pai_asst_preds.append(pai_pred)
            if pai_pred == 1:
                c_pai_blocked = True

            conv_turns_log.append({
                "turn_index": t_idx,
                "role": role,
                "content_preview": content[:60] + "..." if len(content) > 60 else content,
                "guardshield_risk": round(gs_risk, 4),
                "guardshield_pred": gs_pred,
                "guardshield_signed_history_pred": gs_signed_pred,
                "protectai_risk": round(pai_risk, 4),
                "protectai_pred": pai_pred
            })

        c_gs_raw_blocked = raw_scan["blocked"]
        c_gs_signed_blocked = signed_scan["blocked"]
        if c_gs_raw_blocked: gs_raw_conv_blocked += 1
        if c_gs_signed_blocked: gs_signed_conv_blocked += 1
        if c_pai_blocked: pai_conv_blocked += 1

        detailed_conv_results.append({
            "conversation_id": cid,
            "domain": conv["domain"],
            "turns_count": len(turns),
            "guardshield_raw_blocked": c_gs_raw_blocked,
            "guardshield_signed_blocked": c_gs_signed_blocked,
            "protectai_blocked": c_pai_blocked,
            "turns": conv_turns_log
        })

    total_turns = len(gs_all_preds)
    total_users = len(gs_user_preds)
    total_assts = len(gs_asst_preds)
    total_convs = len(conversations)

    # Compute FPRs
    gs_raw_turn_fpr = sum(gs_all_preds) / total_turns
    gs_user_turn_fpr = sum(gs_user_preds) / total_users
    gs_asst_turn_fpr = sum(gs_asst_preds) / total_assts

    gs_raw_conv_fpr = gs_raw_conv_blocked / total_convs
    gs_signed_conv_fpr = gs_signed_conv_blocked / total_convs

    pai_turn_fpr = sum(pai_all_preds) / total_turns
    pai_user_turn_fpr = sum(pai_user_preds) / total_users
    pai_asst_turn_fpr = sum(pai_asst_preds) / total_assts
    pai_conv_fpr = pai_conv_blocked / total_convs

    output = {
        "metadata": {
            "benchmark_name": "GuardShield Multi-Turn Dialogue Benign Benchmark",
            "dataset_sha256": compute_sha256(DATA_FILE),
            "git_commit": get_git_commit(),
            "weights_sha256": weights_sha256(guardshield_engine.model_dir),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "device": device.upper(),
            "device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU",
            "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
            "torch_version": torch.__version__,
            "transformers_version": transformers.__version__,
            "sample_conversations": total_convs,
            "sample_turns": total_turns,
            "user_turns": total_users,
            "assistant_turns": total_assts,
            "guardshield_scan_logic": "proxy_server.scan_messages (short-turn context, max-risk)"
        },
        "guardshield_eval": {
            "all_turns_fpr": round(float(gs_raw_turn_fpr), 4),
            "all_turns_false_positives": int(sum(gs_all_preds)),
            "user_turns_fpr": round(float(gs_user_turn_fpr), 4),
            "user_turns_false_positives": int(sum(gs_user_preds)),
            "assistant_turns_fpr": round(float(gs_asst_turn_fpr), 4),
            "assistant_turns_false_positives": int(sum(gs_asst_preds)),
            "raw_conversation_fpr": round(float(gs_raw_conv_fpr), 4),
            "raw_conversations_blocked": int(gs_raw_conv_blocked),
            "signed_history_user_turns_fpr": round(float(sum(gs_signed_user_preds) / total_users), 4),
            "signed_history_user_turns_false_positives": int(sum(gs_signed_user_preds)),
            "signed_history_conversation_fpr": round(float(gs_signed_conv_fpr), 4),
            "signed_history_conversations_blocked": int(gs_signed_conv_blocked)
        },
        "protectai_eval": {
            "all_turns_fpr": round(float(pai_turn_fpr), 4),
            "all_turns_false_positives": int(sum(pai_all_preds)),
            "user_turns_fpr": round(float(pai_user_turn_fpr), 4),
            "user_turns_false_positives": int(sum(pai_user_preds)),
            "assistant_turns_fpr": round(float(pai_asst_turn_fpr), 4),
            "assistant_turns_false_positives": int(sum(pai_asst_preds)),
            "conversation_fpr": round(float(pai_conv_fpr), 4),
            "conversations_blocked": int(pai_conv_blocked)
        },
        "detailed_conversations": detailed_conv_results
    }

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print("  Multi-Turn Benchmark Results Summary")
    print("=" * 80)
    print(f"Total Conversations: {total_convs} | Total Turns: {total_turns} ({total_users} user, {total_assts} assistant)")
    print("\n[GuardShield AI (Ours)]:")
    print(f"  • Raw All-Turns FPR:                {gs_raw_turn_fpr*100:.2f}% ({sum(gs_all_preds)}/{total_turns})")
    print(f"  • User-Turns FPR:                   {gs_user_turn_fpr*100:.2f}% ({sum(gs_user_preds)}/{total_users})")
    print(f"  • Assistant-Turns FPR:              {gs_asst_turn_fpr*100:.2f}% ({sum(gs_asst_preds)}/{total_assts})")
    print(f"  • Raw Conversation Block Rate:      {gs_raw_conv_fpr*100:.2f}% ({gs_raw_conv_blocked}/{total_convs})")
    print(f"  • Signed History Conv Block Rate:   {gs_signed_conv_fpr*100:.2f}% ({gs_signed_conv_blocked}/{total_convs})")
    print("\n[ProtectAI DeBERTa-v3-base (External SLM)]:")
    print(f"  • All-Turns FPR:                    {pai_turn_fpr*100:.2f}% ({sum(pai_all_preds)}/{total_turns})")
    print(f"  • User-Turns FPR:                   {pai_user_turn_fpr*100:.2f}% ({sum(pai_user_preds)}/{total_users})")
    print(f"  • Assistant-Turns FPR:              {pai_asst_turn_fpr*100:.2f}% ({sum(pai_asst_preds)}/{total_assts})")
    print(f"  • Conversation Block Rate:          {pai_conv_fpr*100:.2f}% ({pai_conv_blocked}/{total_convs})")
    print("=" * 80 + "\n")
    print(f"Saved multi-turn evaluation report -> {OUT_FILE}")

if __name__ == "__main__":
    evaluate_multiturn()
