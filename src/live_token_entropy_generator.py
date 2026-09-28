import os
import sys
import math
import argparse
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

def run_live_entropy_stream(prompt: str, max_new_tokens: int = 15, entropy_threshold: float = 1.25, model_name: str = "gpt2"):
    print("\n" + "=" * 78)
    print("  GuardShield AI — Live Dynamic Token Entropy Stream (Real Neural Network)")
    print("=" * 78)
    print(f"Model:  {model_name}")
    print(f"Prompt: {repr(prompt)}\n")
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if device == "cuda" else torch.float32
    
    print(f"Loading Generative Model ({model_name}) on {device.upper()} with dtype={torch_dtype}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch_dtype,
        trust_remote_code=True
    ).to(device)
    model.eval()
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Apply chat template if available
    if hasattr(tokenizer, "apply_chat_template") and tokenizer.chat_template:
        messages = [{"role": "user", "content": prompt}]
        formatted_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    else:
        formatted_prompt = prompt
        
    input_ids = tokenizer(formatted_prompt, return_tensors="pt").input_ids.to(device)
    
    print(f"\n{'Generated Token':<16} | {'Top-3 Dynamic Probabilities':<30} | {'Entropy H(x)':<12} | {'Status'}")
    print("-" * 78)
    
    consecutive_spikes = 0
    current_input_ids = input_ids
    
    for step in range(max_new_tokens):
        with torch.no_grad():
            outputs = model(current_input_ids)
            next_token_logits = outputs.logits[:, -1, :]
            
            # Softmax over vocabulary
            probs = torch.softmax(next_token_logits, dim=-1)[0]
            
            # Extract dynamic top-3 candidates
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
            
            display_tok = token_str.replace("\n", "\\n").strip() or "<sp>"
            print(f"{repr(display_tok):<16} | {str(normalized_top):<30} | {h:<12} | {status}")
            
            if consecutive_spikes >= 2:
                print("-" * 78)
                print(">> [EARLY TERMINATION TRIGGERED] Live generation halted on sustained uncertainty!")
                break
                
            current_input_ids = torch.cat([current_input_ids, next_token_id], dim=-1)
            
    print("=" * 78 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GuardShield AI - Live Dynamic Token Entropy Stream")
    parser.add_argument("--model", type=str, default="gpt2", help="Model name (e.g. gpt2, Qwen/Qwen2.5-0.5B-Instruct)")
    parser.add_argument("--prompt", type=str, default="The capital of France is", help="Input prompt")
    parser.add_argument("--tokens", type=int, default=10, help="Max new tokens")
    parser.add_argument("--threshold", type=float, default=1.25, help="Entropy spike threshold")
    args = parser.parse_args()
    
    run_live_entropy_stream(prompt=args.prompt, max_new_tokens=args.tokens, entropy_threshold=args.threshold, model_name=args.model)
