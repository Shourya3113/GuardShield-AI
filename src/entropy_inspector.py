import sys
import math
from typing import List, Dict, Any

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def compute_shannon_entropy(probabilities: List[float]) -> float:
    """
    Computes Shannon Entropy H(x) = -sum(p(x) * log2(p(x)))
    over a list of token probabilities.
    
    Higher entropy indicates higher model uncertainty (potential hallucination).
    """
    if not probabilities:
        return 0.0
    
    total_p = sum(probabilities)
    if total_p == 0:
        return 0.0
    
    norm_probs = [p / total_p for p in probabilities if p > 0]
    
    entropy = -sum(p * math.log2(p) for p in norm_probs)
    return round(entropy, 4)

def inspect_token_stream_entropy(tokens_with_probs: List[Dict[str, Any]], entropy_threshold: float = 1.5):
    """
    Iterates through a streaming list of generated tokens,
    computes logit entropy per token, and flags uncertainty spikes.
    """
    results = []
    print("=" * 65)
    print("  [GuardShield AI] Streaming Token Logit Entropy Inspection")
    print("=" * 65)
    print(f"{'Token':<18} | {'Probabilities':<25} | {'Entropy H(x)':<12} | {'Status'}")
    print("-" * 65)
    
    for item in tokens_with_probs:
        token = item.get("token", "")
        probs = item.get("probs", [1.0])
        entropy = compute_shannon_entropy(probs)
        
        is_uncertain = entropy > entropy_threshold
        status = "[WARN] SPIKE (Check NLI)" if is_uncertain else "[OK]"
        
        print(f"{repr(token):<18} | {str([round(p, 2) for p in probs]):<25} | {entropy:<12.4f} | {status}")
        
        results.append({
            "token": token,
            "entropy": entropy,
            "is_uncertain": is_uncertain
        })
        
    print("=" * 65 + "\n")
    return results

if __name__ == "__main__":
    # Test prototype with synthetic token probability distributions
    mock_streaming_tokens = [
        {"token": "GuardShield", "probs": [0.95, 0.03, 0.02]},
        {"token": " AI", "probs": [0.98, 0.01, 0.01]},
        {"token": " runs", "probs": [0.92, 0.05, 0.03]},
        {"token": " on", "probs": [0.89, 0.08, 0.03]},
        {"token": " quantum", "probs": [0.33, 0.33, 0.34]},  # High uncertainty spike!
        {"token": " hardware", "probs": [0.40, 0.35, 0.25]}   # High uncertainty spike!
    ]
    
    inspect_token_stream_entropy(mock_streaming_tokens, entropy_threshold=1.5)
