"""
Model access for the dashboard: the GuardShield pipeline (loaded once per server) and the optional Ollama generator.
"""

import contextlib
import io
import json
import sys
from pathlib import Path
from typing import Iterator, List, Optional, Tuple

import httpx
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

DEFAULT_OLLAMA_URL = "http://localhost:11434/v1"


@st.cache_resource(show_spinner="Loading GuardShield: Stage 1 classifier, Qwen2.5-0.5B generator, Stage 2 verifier…")
def get_pipeline():
    from guardshield_unified_pipeline import GuardShieldPipeline
    with contextlib.redirect_stdout(io.StringIO()):  # the pipeline narrates to the terminal; the dashboard shows it instead
        return GuardShieldPipeline()


@st.cache_resource(show_spinner="Warming up the GPU so the first live prompt is as fast as the rest…")
def warmed_pipeline(warm_texts: Tuple[str, ...]):
    """The pipeline after one pass over the demo prompts. The first call at each new input length is several times
    slower on the GPU, so without this the first live prompt would show a misleading latency."""
    pipeline = get_pipeline()
    with contextlib.redirect_stdout(io.StringIO()):
        for _ in range(3):
            for text in warm_texts:
                pipeline.prescan.inspect_prompt(text)
        pipeline.nli.verify_claim(warm_texts[0], warm_texts[0])
        pipeline.run("What is the capital of France?", reference_context="Paris is the capital of France.", max_new_tokens=8)
    return pipeline


@st.cache_resource
def proxy():
    """The proxy module, for scan_messages, the HMAC signing helpers and the logprob parser."""
    import proxy_server
    return proxy_server


def configure(pipeline, stage1: float, entropy: float, spikes: int) -> None:
    pipeline.prescan_threshold = stage1
    pipeline.prescan.threshold = stage1
    pipeline.entropy_threshold = entropy
    pipeline.consecutive_spikes_limit = spikes


def run_pipeline(pipeline, prompt: str, context: Optional[str], max_tokens: int, on_token=None, token_source=None):
    with contextlib.redirect_stdout(io.StringIO()):
        return pipeline.run(prompt, reference_context=context or None, max_new_tokens=max_tokens,
                            on_token=on_token, token_source=token_source)


WAKE_SECONDS = 0.4


def wake_gpu(pipeline, text: str, seconds: float = WAKE_SECONDS) -> None:
    """An idle laptop GPU drops its clocks within seconds, and its next request then runs about 4x slower (measured:
    ~29 ms back to back, ~138 ms after a 4 s pause). A loaded server never idles, so before each timed demo request
    the GPU is kept busy for 0.4 s, after which Stage 1 is back at 24-32 ms."""
    import time
    start = time.perf_counter()
    with contextlib.redirect_stdout(io.StringIO()):
        while time.perf_counter() - start < seconds:
            pipeline.prescan.inspect_prompt(text)


def scan(pipeline, prompt: str):
    with contextlib.redirect_stdout(io.StringIO()):
        return pipeline.prescan.inspect_prompt(prompt)


# --------------------------------------------------------------------------- Ollama
@st.cache_data(ttl=30, show_spinner=False)  # asked on every rerun otherwise, which slows each click by ~2 s
def ollama_models(url: str) -> List[str]:
    """Installed Ollama models, or an empty list if the server is not running."""
    base = url.rstrip("/").removesuffix("/v1")
    try:
        r = httpx.get(f"{base}/api/tags", timeout=2.0)
        r.raise_for_status()
        return sorted(m["name"] for m in r.json().get("models", []))
    except (httpx.HTTPError, ValueError):
        return []


def ollama_stream(url: str, model: str, prompt: str, max_tokens: int) -> Iterator[Tuple[str, Optional[List[float]]]]:
    """Streams (text chunk, top-3 probabilities or None) from Ollama's OpenAI-compatible endpoint, greedily."""
    payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "stream": True, "temperature": 0,
               "max_tokens": max_tokens, "logprobs": True, "top_logprobs": 3}
    top_probs = proxy().top_probs_from_choice
    with httpx.stream("POST", f"{url.rstrip('/')}/chat/completions", json=payload, timeout=120.0) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if not line.startswith("data: "):
                continue
            data = line[6:].strip()
            if data == "[DONE]":
                break
            choice = (json.loads(data).get("choices") or [{}])[0]
            chunk = (choice.get("delta") or {}).get("content")
            if chunk:
                yield chunk, (top_probs(choice) or None)
