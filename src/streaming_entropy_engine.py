import sys
import math
import time
import logging
from typing import List, Dict, Any, Tuple

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("StreamingEntropyEngine")

class StreamingEntropyEngine:
    """
    Real-Time Streaming Token Logit Entropy Inspector & Early Termination Controller.
    Computes Shannon Entropy H(x) = -sum(p * log2(p)) over discrete token probability distributions.
    Triggers early token termination when sustained entropy spikes indicate model hallucination drift.
    """
    def __init__(self, spike_threshold: float = 1.20, consecutive_spike_limit: int = 2):
        self.spike_threshold = spike_threshold
        self.consecutive_spike_limit = consecutive_spike_limit
        self.consecutive_spikes = 0
        self.history = []

    def compute_entropy(self, probabilities: List[float]) -> float:
        """
        Calculate Shannon Entropy in bits: H(x) = -sum(p * log2(p))
        """
        entropy = 0.0
        for p in probabilities:
            if p > 1e-7:
                entropy -= p * math.log2(p)
        return round(entropy, 4)

    def process_token(self, token: str, top_probabilities: List[float]) -> Dict[str, Any]:
        """
        Process a single streaming token and return status and early termination signal.
        """
        entropy = self.compute_entropy(top_probabilities)
        is_spike = entropy >= self.spike_threshold
        
        if is_spike:
            self.consecutive_spikes += 1
        else:
            self.consecutive_spikes = 0
            
        should_terminate = self.consecutive_spikes >= self.consecutive_spike_limit
        
        record = {
            "token": token,
            "probabilities": top_probabilities,
            "entropy": entropy,
            "is_spike": is_spike,
            "consecutive_spikes": self.consecutive_spikes,
            "should_terminate": should_terminate,
            "status": "TERMINATE_EARLY (Hallucination Detected)" if should_terminate else ("WARN_SPIKE" if is_spike else "OK")
        }
        self.history.append(record)
        return record

    def reset(self):
        """Reset state between streaming queries."""
        self.consecutive_spikes = 0
        self.history = []

if __name__ == "__main__":
    engine = StreamingEntropyEngine(spike_threshold=1.20, consecutive_spike_limit=2)
    
    # Simulated token stream: factual beginning followed by hallucination drift
    simulated_stream = [
        ("The", [0.96, 0.03, 0.01]),
        (" capital", [0.94, 0.04, 0.02]),
        (" of", [0.98, 0.01, 0.01]),
        (" France", [0.95, 0.03, 0.02]),
        (" is", [0.97, 0.02, 0.01]),
        (" Paris,", [0.93, 0.05, 0.02]),
        (" which", [0.90, 0.06, 0.04]),
        (" was", [0.88, 0.08, 0.04]),
        (" founded", [0.85, 0.10, 0.05]),
        (" by", [0.82, 0.12, 0.06]),
        (" quantum", [0.34, 0.33, 0.33]),   # Spike 1 (Uncertainty / Hallucination)
        (" astronauts", [0.35, 0.35, 0.30]) # Spike 2 (Sustained -> Trigger Early Termination!)
    ]
    
    print("\n" + "=" * 75)
    print("  [GuardShield AI] Live Streaming Token Entropy & Early Termination Demo")
    print("=" * 75)
    print(f"{'Token':<15} | {'Probabilities':<20} | {'Entropy H(x)':<12} | {'Action'}")
    print("-" * 75)
    
    for token, probs in simulated_stream:
        res = engine.process_token(token, probs)
        print(f"{repr(res['token']):<15} | {str(res['probabilities']):<20} | {res['entropy']:<12} | {res['status']}")
        if res["should_terminate"]:
            print("-" * 75)
            print("🚨 EARLY TERMINATION TRIGGERED: Stream halted before delivering hallucinated text!")
            break
            
    print("=" * 75 + "\n")
