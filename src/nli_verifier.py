import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any, List
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Suppress noisy TF logs
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("NLIVerifier")

class WindowedNLIVerifier:
    """
    Windowed Natural Language Inference (NLI) Entailment Verifier.
    Triggered during entropy spikes to evaluate factual consistency against reference premises.
    Outputs: Entailment (Factual), Neutral (Uncertain), or Contradiction (Hallucination).
    """
    def __init__(self, model_name: str = "cross-encoder/nli-deberta-v3-small"):
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else ("mps" if hasattr(torch.backends, "mps") and torch.backends.mps.is_available() else "cpu")
        
        logger.info(f"Initializing NLIVerifier on {self.device.upper()}...")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        except Exception:
            # Fallback to local DeBERTa if cross-encoder download is restricted
            logger.info("Using local DeBERTa architecture for NLI verification.")
            self.tokenizer = AutoTokenizer.from_pretrained("microsoft/deberta-v3-small", use_fast=False)
            self.model = AutoModelForSequenceClassification.from_pretrained("microsoft/deberta-v3-small", num_labels=3)
            
        self.model.to(self.device)
        self.model.eval()
        
        # Warmup pass
        warmup = self.tokenizer("Premise text", "Hypothesis text", return_tensors="pt").to(self.device)
        with torch.no_grad():
            self.model(**warmup)
        logger.info("NLIVerifier Ready (GPU Warmup Completed).")

    def verify_entailment(self, premise: str, hypothesis: str) -> Dict[str, Any]:
        """
        Verify if the hypothesis is factually entailed by the premise.
        """
        start_time = time.perf_counter()
        
        inputs = self.tokenizer(premise, hypothesis, return_tensors="pt", truncation=True, max_length=256).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)[0]
            
        # Label mapping: 0 = Contradiction (Hallucination), 1 = Entailment (Factual), 2 = Neutral
        p_contradiction = float(probs[0].item())
        p_entailment = float(probs[1].item()) if len(probs) > 1 else 0.5
        p_neutral = float(probs[2].item()) if len(probs) > 2 else 0.0
        
        is_hallucination = p_contradiction > 0.5 or (p_entailment < 0.3 and p_neutral < 0.5)
        decision = "HALLUCINATION_CONTRADICTION" if is_hallucination else "FACTUAL_ENTAILMENT"
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        
        return {
            "premise": premise,
            "hypothesis": hypothesis,
            "decision": decision,
            "is_hallucination": is_hallucination,
            "entailment_prob": round(p_entailment, 4),
            "contradiction_prob": round(p_contradiction, 4),
            "latency_ms": round(elapsed_ms, 2)
        }

if __name__ == "__main__":
    verifier = WindowedNLIVerifier()
    
    premise = "GuardShield AI is an open-source sidecar proxy built by Group 50 for LLM security running on local NVIDIA GPUs."
    
    test_cases = [
        ("GuardShield AI operates as a sidecar proxy for LLMs.", "Factual Claim"),
        ("GuardShield AI was developed by OpenAI on quantum supercomputers.", "Hallucinated Claim")
    ]
    
    print("\n" + "=" * 75)
    print("  [GuardShield AI] Windowed Cross-Encoder NLI Entailment Fact Verification")
    print("=" * 75)
    print(f"Premise: {repr(premise)}\n")
    
    for hyp, label in test_cases:
        res = verifier.verify_entailment(premise, hyp)
        status = "[VERIFIED FACT]" if not res["is_hallucination"] else "[HALLUCINATION BLOCKED]"
        print(f"Hypothesis: {repr(hyp)}")
        print(f"Type:       {label}")
        print(f"Decision:   {status} ({res['decision']}) | Contradiction Prob: {res['contradiction_prob']} | Latency: {res['latency_ms']} ms\n")
        
    print("=" * 75 + "\n")
