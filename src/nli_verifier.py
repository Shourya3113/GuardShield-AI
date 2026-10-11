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

sys.path.append(str(Path(__file__).resolve().parent))
import config

class WindowedNLIVerifier:
    """
    Windowed Natural Language Inference (NLI) Entailment Verifier.
    Triggered during entropy spikes to evaluate factual consistency against reference premises.
    Outputs: Entailment (Factual), Neutral (Uncertain), or Contradiction (Hallucination).
    """
    def __init__(self, model_name: str = "cross-encoder/nli-deberta-v3-small", threshold: float = 0.50):
        self.model_name = model_name
        self.threshold = threshold
        self.device = "cuda" if torch.cuda.is_available() else ("mps" if hasattr(torch.backends, "mps") and torch.backends.mps.is_available() else "cpu")
        
        logger.info(f"Initializing NLIVerifier on {self.device.upper()}...")
        loaded = False

        # 1. Try local cache first for air-gapped / offline reproducibility
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False, local_files_only=True)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name, local_files_only=True)
            loaded = True
            logger.info(f"Loaded {model_name} from local cache (Air-Gapped Mode).")
        except Exception:
            pass

        # 2. Check network connectivity with fast 1.5s timeout before attempting online HuggingFace fetch
        if not loaded:
            import socket
            is_online = False
            try:
                s = socket.create_connection(("huggingface.co", 443), timeout=1.5)
                s.close()
                is_online = True
            except Exception:
                is_online = False

            if is_online:
                try:
                    self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
                    self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
                    loaded = True
                except Exception as exc:
                    logger.warning(f"Failed to fetch {model_name} online: {exc}")
            else:
                logger.warning(f"Host offline: Skipping remote HuggingFace download for {model_name}.")

        # 3. Strict failure if model cannot be loaded (no silent untrained fallback)
        if not loaded:
            raise RuntimeError(
                f"Failed to load NLI verifier model '{model_name}'. "
                "In offline or air-gapped environments, please ensure pre-cached weights are available, "
                "or connect to the internet to download the cross-encoder checkpoint."
            )
            
        self.model.to(self.device)
        self.model.eval()
        
        # Dynamically resolve label indices from model configuration
        id2label = getattr(self.model.config, "id2label", {})
        self.contra_idx = 0
        self.entail_idx = 1
        self.neutral_idx = 2
        if id2label:
            for idx, label in id2label.items():
                lbl = str(label).lower()
                if "contra" in lbl:
                    self.contra_idx = int(idx)
                elif "entail" in lbl:
                    self.entail_idx = int(idx)
                elif "neut" in lbl:
                    self.neutral_idx = int(idx)
        logger.info(f"NLI Label Mapping: Contradiction={self.contra_idx}, Entailment={self.entail_idx}, Neutral={self.neutral_idx}")
        
        # Warmup pass
        warmup = self.tokenizer("Premise text", "Hypothesis text", return_tensors="pt").to(self.device)
        with torch.no_grad():
            self.model(**warmup)
        logger.info("NLIVerifier Ready (GPU Warmup Completed).")

    def verify_claim(self, premise: str, hypothesis: str) -> Dict[str, Any]:
        """
        Runs claim-level windowed NLI verification.
        Splits multi-sentence hypotheses into declarative sentences.
        Requires all asserted claims to be factually entailed; any contradictory
        claim flags hard hallucination. Neutral claims without sufficient evidence
        are classified as UNVERIFIED_NEUTRAL rather than conflated with hallucinations.
        """
        import re
        raw_sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', hypothesis) if s.strip()]
        sentences = [
            s for s in raw_sentences 
            if len(s.split()) >= 3 or s.endswith(('.', '!', '?'))
        ]
        if not sentences:
            sentences = [hypothesis]

        if len(sentences) == 1:
            return self.verify_entailment(premise, sentences[0])

        # Multi-sentence verification
        start_time = time.perf_counter()
        sent_results = [self.verify_entailment(premise, s) for s in sentences]

        # 1. Any sentence directly contradicting the premise marks a hallucination
        contradictions = [r for r in sent_results if r["is_contradiction"]]
        if contradictions:
            worst = max(contradictions, key=lambda r: r["contradiction_prob"])
            worst["latency_ms"] = round((time.perf_counter() - start_time) * 1000.0, 2)
            worst["hypothesis"] = hypothesis
            return worst

        # 2. Strict factuality: All sentences must be entailed
        all_entailed = all(r["decision"] == "FACTUAL_ENTAILMENT" for r in sent_results)
        if all_entailed:
            min_entail = min(sent_results, key=lambda r: r["entailment_prob"])
            min_entail["latency_ms"] = round((time.perf_counter() - start_time) * 1000.0, 2)
            min_entail["hypothesis"] = hypothesis
            return min_entail

        # 3. If no contradiction but not all entailed, claim is unverified / insufficient context
        avg_contra = sum(r["contradiction_prob"] for r in sent_results) / len(sent_results)
        avg_entail = sum(r["entailment_prob"] for r in sent_results) / len(sent_results)
        avg_neutral = sum(r["neutral_prob"] for r in sent_results) / len(sent_results)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return {
            "premise": premise,
            "hypothesis": hypothesis,
            "decision": "UNVERIFIED_NEUTRAL",
            "is_hallucination": False,
            "is_contradiction": False,
            "is_unverified": True,
            "entailment_prob": round(avg_entail, 4),
            "contradiction_prob": round(avg_contra, 4),
            "neutral_prob": round(avg_neutral, 4),
            "latency_ms": round(elapsed_ms, 2)
        }

    def verify_entailment(self, premise: str, hypothesis: str) -> Dict[str, Any]:
        """
        Verify if the hypothesis is factually entailed by the premise.
        Distinguishes Contradiction (Hallucination), Entailment (Supported), and Neutral (Unverified).
        """
        start_time = time.perf_counter()
        
        inputs = self.tokenizer(premise, hypothesis, return_tensors="pt", truncation=True, max_length=256).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)[0]
            
        p_contradiction = float(probs[self.contra_idx].item()) if len(probs) > self.contra_idx else 0.0
        p_entailment = float(probs[self.entail_idx].item()) if len(probs) > self.entail_idx else 0.0
        p_neutral = float(probs[self.neutral_idx].item()) if len(probs) > self.neutral_idx else 0.0

        # Rigorous Factual Verification:
        if p_contradiction >= self.threshold:
            decision = "HALLUCINATION_CONTRADICTION"
            is_hallucination = True
            is_contradiction = True
            is_unverified = False
        elif p_entailment >= self.threshold:
            decision = "FACTUAL_ENTAILMENT"
            is_hallucination = False
            is_contradiction = False
            is_unverified = False
        else:
            decision = "UNVERIFIED_NEUTRAL"
            is_hallucination = False
            is_contradiction = False
            is_unverified = True

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return {
            "premise": premise,
            "hypothesis": hypothesis,
            "decision": decision,
            "is_hallucination": is_hallucination,
            "is_contradiction": is_contradiction,
            "is_unverified": is_unverified,
            "entailment_prob": round(p_entailment, 4),
            "contradiction_prob": round(p_contradiction, 4),
            "neutral_prob": round(p_neutral, 4),
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
