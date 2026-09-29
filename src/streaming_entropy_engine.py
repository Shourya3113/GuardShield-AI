import sys
import math
import time
import logging
from typing import List, Dict, Any, Tuple, Optional

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
    def __init__(
        self,
        spike_threshold: float = 1.25,
        consecutive_spike_limit: int = 2,
        vocab_size: Optional[int] = None,
        mode: str = "normalized_top_k"
    ):
        """
        Initialize the Streaming Entropy Engine.
        :param spike_threshold: Entropy threshold in bits to trigger an uncertainty spike.
                                For top-3 normalized probabilities (max entropy = log2(3) = 1.585 bits),
                                1.25 bits (~79% of max uncertainty) reliably separates factual tokens
                                (e.g. [0.6, 0.2, 0.1] -> 1.22 bits, [0.95, 0.03, 0.02] -> 0.33 bits)
                                from flat uncertainty (e.g. [0.34, 0.33, 0.33] -> 1.585 bits).
        :param consecutive_spike_limit: Number of consecutive spikes before triggering early termination.
        :param vocab_size: Optional vocabulary size (e.g. 32000 for LLaMA, 151936 for Qwen2.5) if
                           using open-vocabulary tail-mass mode.
        :param mode: 'normalized_top_k' (default, model-agnostic, bounded in [0, log2(k)]) or
                     'open_vocab_tail' (accounts for tail mass over vocab_size, with open-vocab threshold).
        """
        self.spike_threshold = spike_threshold
        self.consecutive_spike_limit = consecutive_spike_limit
        self.vocab_size = vocab_size
        self.mode = mode
        self.consecutive_spikes = 0
        self.history = []

    def compute_entropy(
        self,
        probabilities: List[float],
        vocab_size: Optional[int] = None
    ) -> float:
        """
        Calculate Shannon Entropy in bits: H(x) = -sum(p * log2(p)).
        When given top-k probabilities (k >= 2), renormalizes the distribution over the candidate set
        so entropy is strictly bounded in [0, log2(k)] and independent of arbitrary vocab sizes.
        """
        valid_probs = [max(1e-12, float(p)) for p in probabilities if p > 0]
        if not valid_probs:
            return 0.0
            
        effective_vocab = vocab_size or self.vocab_size
        
        # If open_vocab_tail mode is explicitly requested and vocab_size is available
        if self.mode == "open_vocab_tail" and effective_vocab and effective_vocab > len(valid_probs):
            known_mass = min(1.0, sum(valid_probs))
            tail_mass = max(0.0, 1.0 - known_mass)
            entropy = 0.0
            for p in valid_probs:
                entropy -= p * math.log2(p)
            if tail_mass > 1e-4:
                remaining_tokens = max(1, effective_vocab - len(valid_probs))
                p_tail_avg = tail_mass / remaining_tokens
                entropy -= tail_mass * math.log2(p_tail_avg)
            return round(entropy, 4)
            
        # Default: Normalized top-k conditional Shannon entropy
        # Invariant to vocab size, bounded in [0, log2(k)]
        total_mass = sum(valid_probs)
        normalized = [p / total_mass for p in valid_probs]
        
        entropy = 0.0
        for p in normalized:
            if p > 1e-12:
                entropy -= p * math.log2(p)
                
        return round(entropy, 4)

    def compute_entropy_from_logits(self, logits) -> float:
        """
        Calculate exact Shannon Entropy across the entire open vocabulary directly from unnormalized logits.
        Supports PyTorch tensors, NumPy arrays, or lists of floats.
        """
        try:
            import torch
            if isinstance(logits, torch.Tensor):
                probs = torch.softmax(logits, dim=-1)
                log_probs = torch.log2(torch.clamp(probs, min=1e-12))
                entropy = -(probs * log_probs).sum().item()
                return round(float(entropy), 4)
        except ImportError:
            pass

        # NumPy fallback
        import numpy as np
        arr = np.array(logits, dtype=np.float64)
        exp_arr = np.exp(arr - np.max(arr))
        probs = exp_arr / np.sum(exp_arr)
        probs = np.clip(probs, 1e-12, 1.0)
        entropy = -np.sum(probs * np.log2(probs))
        return round(float(entropy), 4)

    def process_token(
        self,
        token: str,
        top_probabilities: List[float],
        vocab_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process a single streaming token and return status and early termination signal.
        """
        entropy = self.compute_entropy(top_probabilities, vocab_size=vocab_size)
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
    engine = StreamingEntropyEngine(spike_threshold=1.25, consecutive_spike_limit=2)
    
    # Realistic test distributions
    test_cases = [
        ("The", [0.95, 0.03, 0.02]),          # Confident -> low entropy (~0.33 bits)
        (" capital", [0.60, 0.20, 0.10]),      # Realistic top-1 60% -> 1.22 bits (below 1.25 threshold!)
        (" quantum", [0.34, 0.33, 0.33]),      # Flat uncertainty -> 1.58 bits (Spike 1)
        (" astronauts", [0.35, 0.35, 0.30])    # Sustained uncertainty -> Spike 2 -> Early termination!
    ]
    
    print("\n" + "=" * 80)
    print("  [GuardShield AI] Live Streaming Token Entropy Verification")
    print("=" * 80)
    print(f"{'Token':<15} | {'Probabilities':<22} | {'Entropy H(x)':<14} | {'Status'}")
    print("-" * 80)
    for tok, probs in test_cases:
        res = engine.process_token(tok, probs)
        print(f"{tok:<15} | {str(probs):<22} | {res['entropy']:<14} | {res['status']}")
    print("=" * 80 + "\n")
