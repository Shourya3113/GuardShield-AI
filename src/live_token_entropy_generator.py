import os
import sys
import math
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def compute_entropy(probabilities):
    h = 0.0
    for p in probabilities:
        if p > 1e-7:
            h -= p * math.log2(p)
    return round(h, 4)

def run_live_entropy_stream(prompt: str, max_new_tokens: int = 15, entropy_threshold: float = 1.25):
    print("\n" + "=" * 78)
    print("  GuardShield AI — Live Dynamic Token Entropy Stream (Real Neural Network)")
    print("=" * 78)
    print(f"Prompt: {repr(prompt)}\n")
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model_name = "gpt2"
    
    print(f"Loading Generative Model ({model_name}) on {device.upper()}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
    model.eval()
    
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)
    
    print(f"\n{'Generated Token':<16} | {'Top-3 Dynamic Probabilities':<30} | {'Entropy H(x)':<12} | {'Status'}")
    print("-" * 78)
    
    consecutive_spikes = 0
    current_input_ids = input_ids
    
    for step in range(max_new_tokens):
        with torch.no_grad():
            outputs = model(current_input_ids)
            next_token_logits = outputs.logits[:, -1, :]
            
            # Real Softmax over vocabulary
            probs = torch.softmax(next_token_logits, dim=-1)[0]
            
            # Extract real dynamic top-3 candidates
            top_k_probs, top_k_indices = torch.topk(probs, k=3)
            
            top_probs_list = [round(float(p), 4) for p in top_k_probs.tolist()]
            
            # Normalize top-3 for local conditional entropy
            sum_top = sum(top_probs_list)
            normalized_top = [round(p / sum_top, 4) for p in top_probs_list]
            
            # Pick greedy next token
            next_token_id = top_k_indices[0].unsqueeze(0).unsqueeze(0)
            token_str = tokenizer.decode(next_token_id[0][0])
            
            # Compute Shannon Entropy dynamically
            h = compute_entropy(normalized_top)
            
            is_spike = h >= entropy_threshold
            if is_spike:
                consecutive_spikes += 1
            else:
                consecutive_spikes = 0
                
            status = "TERMINATE_EARLY" if consecutive_spikes >= 2 else ("WARN_SPIKE" if is_spike else "OK")
            
            print(f"{repr(token_str):<16} | {str(normalized_top):<30} | {h:<12} | {status}")
            
            if consecutive_spikes >= 2:
                print("-" * 78)
                print(">> [EARLY TERMINATION TRIGGERED] Live generation halted on sustained uncertainty!")
                break
                
            current_input_ids = torch.cat([current_input_ids, next_token_id], dim=-1)
            
    print("=" * 78 + "\n")

if __name__ == "__main__":
    test_prompt = "The capital of France is"
    run_live_entropy_stream(test_prompt, max_new_tokens=10)
