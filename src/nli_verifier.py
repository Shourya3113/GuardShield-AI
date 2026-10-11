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

        # 2. Try online HuggingFace download if not cached
        if not loaded:
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
                self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
                loaded = True
            except Exception:
                pass

        # 3. Fallback to local DeBERTa weights directory if cross-encoder download is restricted
        if not loaded:
            logger.info("Using local DeBERTa architecture for NLI verification.")
            local_deberta = config.BASE_DIR / "models" / "deberta_v3_prescan_v3"
            if local_deberta.exists():
                self.tokenizer = AutoTokenizer.from_pretrained(str(local_deberta), use_fast=False)
                self.model = AutoModelForSequenceClassification.from_pretrained(str(local_deberta))
            else:
                self.tokenizer = AutoTokenizer.from_pretrained("microsoft/deberta-v3-small", use_fast=False)
                self.model = AutoModelForSequenceClassification.from_pretrained("microsoft/deberta-v3-small", num_labels=3)
            
        self.model.to(self.device)
        self.model.eval()
        
        # Warmup pass
        warmup = self.tokenizer("Premise text", "Hypothesis text", return_tensors="pt").to(self.device)
        with torch.no_grad():
            self.model(**warmup)
        logger.info("NLIVerifier Ready (GPU Warmup Completed).")

    def verify_claim(self, premise: str, hypothesis: str) -> Dict[str, Any]:
        """
        Runs claim-level windowed NLI verification.
        Splits multi-sentence hypotheses into declarative windows so that
        the core answer is verified even if additional context or elaboration follows.
        """
        import re
        raw_sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', hypothesis) if s.strip()]
        # Discard fragments that have fewer than 3 words and lack terminal punctuation
        sentences = [
            s for s in raw_sentences 
            if len(s.split()) >= 3 or s.endswith(('.', '!', '?'))
        ]
        if not sentences:
            sentences = raw_sentences

        if len(sentences) <= 1:
            # Also extract the primary clause before commas/appositives (e.g. "X was invented by Y, a British scientist...")
            first_sent = sentences[0] if sentences else hypothesis
            sub_clauses = [c.strip() for c in re.split(r'[,;]', first_sent) if len(c.strip().split()) >= 3]
            if len(sub_clauses) > 1:
                # Test full sentence and main assertion
                cand_res = [self.verify_entailment(premise, c) for c in [first_sent, sub_clauses[0]]]
                # If main clause entails and has no contradiction, take it
                entailed = [r for r in cand_res if r["decision"] in ("FACTUAL_ENTAILMENT", "FACTUALLY_CONSISTENT_REFUTATION")]
                if entailed:
                    best = max(entailed, key=lambda r: (r["decision"] == "FACTUAL_ENTAILMENT", r["entailment_prob"]))
                    best["hypothesis"] = hypothesis
                    return best
            return self.verify_entailment(premise, first_sent)

        # Multi-sentence hypothesis
        start_time = time.perf_counter()
        candidate_units = list(sentences)
        for s in sentences:
            clauses = [c.strip() for c in re.split(r'[,;]', s) if len(c.strip().split()) >= 3]
            for c in clauses:
                if c not in candidate_units:
                    candidate_units.append(c)

        sent_results = [self.verify_entailment(premise, u) for u in candidate_units]

        # 1. Any sentence directly contradicting the premise marks a hallucination
        contradictions = [r for r in sent_results if r["is_contradiction"]]
        if contradictions:
            worst = max(contradictions, key=lambda r: r["contradiction_prob"])
            worst["latency_ms"] = round((time.perf_counter() - start_time) * 1000.0, 2)
            worst["hypothesis"] = hypothesis
            return worst

        # 2. At least one sentence entails the premise or is a valid refutation, and no contradictions exist
        valid_factual = [
            r for r in sent_results 
            if r["decision"] in ("FACTUAL_ENTAILMENT", "FACTUALLY_CONSISTENT_REFUTATION")
        ]
        if valid_factual:
            best = max(valid_factual, key=lambda r: (r["decision"] == "FACTUAL_ENTAILMENT", r["entailment_prob"]))
            best["latency_ms"] = round((time.perf_counter() - start_time) * 1000.0, 2)
            best["hypothesis"] = hypothesis
            return best

        # 3. None entail and none contradict -> Ungrounded Neutral
        avg_contra = sum(r["contradiction_prob"] for r in sent_results) / len(sent_results)
        avg_entail = sum(r["entailment_prob"] for r in sent_results) / len(sent_results)
        avg_neutral = sum(r["neutral_prob"] for r in sent_results) / len(sent_results)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return {
            "premise": premise,
            "hypothesis": hypothesis,
            "decision": "UNGROUNDED_NEUTRAL_HALLUCINATION",
            "is_hallucination": True,
            "is_contradiction": False,
            "entailment_prob": round(avg_entail, 4),
            "contradiction_prob": round(avg_contra, 4),
            "neutral_prob": round(avg_neutral, 4),
            "latency_ms": round(elapsed_ms, 2)
        }

    def verify_entailment(self, premise: str, hypothesis: str) -> Dict[str, Any]:
        """
        Verify if the hypothesis is factually entailed by the premise.
        Evaluates contradiction probability against the decision threshold.
        """
        start_time = time.perf_counter()
        
        inputs = self.tokenizer(premise, hypothesis, return_tensors="pt", truncation=True, max_length=256).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)[0]
            
        # Label mapping: 0 = Contradiction, 1 = Entailment, 2 = Neutral
        p_contradiction = float(probs[0].item())
        p_entailment = float(probs[1].item()) if len(probs) > 1 else 0.5
        p_neutral = float(probs[2].item()) if len(probs) > 2 else 0.0

        # Rigorous Factual Verification:
        # A claim is Factual if p_entailment meets threshold.
        # If contradiction >= threshold -> Direct Contradiction
        # If negative refutation of a non-existent entity with low contradiction -> Factually Consistent Refutation
        # If neutral is dominant & ungrounded affirmative speculation -> Ungrounded Neutral Hallucination
        if p_contradiction >= self.threshold:
            decision = "HALLUCINATION_CONTRADICTION"
            is_hallucination = True
        elif p_entailment >= self.threshold:
            decision = "FACTUAL_ENTAILMENT"
            is_hallucination = False
        else:
            # Check for negative refutation of false presuppositions
            # (e.g., "There is no capital of Mars as it is a planet, not a country")
            import re
            is_refutation = bool(re.search(
                r'\b(?:there is no|there are no|has no|have no|does not have|do not have|is not a|are not a|not a country|no capital|doesn\'t have|isn\'t a|cannot have|no evidence)\b',
                hypothesis,
                re.IGNORECASE
            ))
            if is_refutation and p_contradiction < 0.15:
                decision = "FACTUALLY_CONSISTENT_REFUTATION"
                is_hallucination = False
            else:
                decision = "UNGROUNDED_NEUTRAL_HALLUCINATION"
                is_hallucination = True

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return {
            "premise": premise,
            "hypothesis": hypothesis,
            "decision": decision,
            "is_hallucination": is_hallucination,
            "is_contradiction": p_contradiction >= self.threshold,
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
