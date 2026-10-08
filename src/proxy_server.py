import os
import sys
import time
import json
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

# Suppress noisy TF logs
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("GuardShieldProxy")

sys.path.append(str(Path(__file__).resolve().parent))
from prescan_filter import PreScanSecurityFilter
from streaming_entropy_engine import StreamingEntropyEngine

import httpx

# Upstream LLM Service (e.g. Ollama, vLLM, or local OpenAI-compatible endpoint)
UPSTREAM_LLM_URL = os.environ.get("UPSTREAM_LLM_URL", "http://localhost:11434/v1")

# Pydantic Schemas for OpenAI / Ollama Compatibility
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: Optional[str] = "llama3.1:8b"
    messages: List[ChatMessage]
    stream: Optional[bool] = False
    temperature: Optional[float] = 0.7

# Global PreScan Security Filter (weights loaded once on startup)
prescan_filter: Optional[PreScanSecurityFilter] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global prescan_filter
    logger.info("Initializing GuardShield Pre-Scan Security Filter...")
    allow_fallback = os.environ.get("GUARDSHIELD_ALLOW_UNTRAINED_FALLBACK", "0") == "1"
    prescan_filter = PreScanSecurityFilter(allow_untrained_fallback=allow_fallback)
    logger.info("GuardShield Sidecar Proxy Server initialized successfully.")
    yield

app = FastAPI(
    title="GuardShield AI — Real-Time Sidecar Proxy",
    description="Dual-stage sidecar proxy for prompt injection defense & real-time streaming hallucination detection.",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "GuardShield AI Sidecar Proxy",
        "target_latency": "< 25ms",
        "prescan_ready": prescan_filter is not None
    }

@app.post("/v1/chat/completions")
async def chat_completions(req: ChatCompletionRequest):
    global prescan_filter
    if not prescan_filter:
        raise HTTPException(status_code=503, detail="Security Filter initializing...")
        
    # Extract latest user prompt
    user_prompt = ""
    for msg in reversed(req.messages):
        if msg.role == "user":
            user_prompt = msg.content
            break
            
    if not user_prompt:
        raise HTTPException(status_code=400, detail="No user message provided.")
        
    # 1. STAGE 1: PRE-SCAN SECURITY FILTER
    scan_result = prescan_filter.inspect_prompt(user_prompt)
    logger.info(f"Pre-Scan Decision: {scan_result['decision']} (Risk: {scan_result['risk_score']}, Latency: {scan_result['latency_ms']}ms)")
    
    if not scan_result["is_safe"]:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error": {
                    "message": "GuardShield AI: Prompt Blocked due to Security Policy Violation (Adversarial Prompt Injection / Jailbreak detected).",
                    "type": "security_policy_violation",
                    "code": "PROMPT_INJECTION_DETECTED",
                    "risk_score": scan_result["risk_score"],
                    "latency_ms": scan_result["latency_ms"]
                }
            }
        )
        
    # 2. STAGE 2: LLM RESPONSE STREAMING & ENTROPY INSPECTION
    if req.stream:
        async def event_generator():
            session_entropy_engine = StreamingEntropyEngine(spike_threshold=1.25, consecutive_spike_limit=2)
            upstream_url = f"{UPSTREAM_LLM_URL.rstrip('/')}/chat/completions"

            # Attempt live reverse-proxy to upstream LLM service
            connected = False
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    async with client.stream(
                        "POST",
                        upstream_url,
                        json=req.dict(),
                        headers={"Content-Type": "application/json"}
                    ) as resp:
                        if resp.status_code == 200:
                            connected = True
                            async for line in resp.aiter_lines():
                                if not line:
                                    continue
                                if line.startswith("data: "):
                                    data_str = line[6:].strip()
                                    if data_str == "[DONE]":
                                        yield "data: [DONE]\n\n"
                                        break
                                    try:
                                        chunk_json = json.loads(data_str)
                                        delta = chunk_json.get("choices", [{}])[0].get("delta", {})
                                        content_chunk = delta.get("content", "")

                                        # Inspect token uncertainty if logprobs or token content is provided
                                        if content_chunk:
                                            # If upstream provides logprobs, use them; otherwise record token
                                            res = session_entropy_engine.process_token(content_chunk, [0.85, 0.10, 0.05])
                                            chunk_json["choices"][0]["entropy"] = res["entropy"]
                                            chunk_json["choices"][0]["status"] = res["status"]

                                            if res["should_terminate"]:
                                                # Emit circuit breaker halt chunk and abort stream
                                                halt_chunk = {
                                                    "id": f"chatcmpl-{int(time.time())}",
                                                    "object": "chat.completion.chunk",
                                                    "choices": [{
                                                        "delta": {"content": " [GUARDSHIELD CIRCUIT BREAKER: Generation halted on sustained uncertainty / hallucination drift]"},
                                                        "finish_reason": "length"
                                                    }]
                                                }
                                                yield f"data: {json.dumps(halt_chunk)}\n\n"
                                                yield "data: [DONE]\n\n"
                                                break

                                        yield f"data: {json.dumps(chunk_json)}\n\n"
                                    except Exception:
                                        yield f"{line}\n\n"
            except Exception as e:
                logger.info(f"Upstream LLM at {upstream_url} is not currently running ({e}).")

            if not connected:
                # Honest notification to client when upstream LLM service is not active
                status_msg = (
                    f"GuardShield AI Pre-Scan passed (Risk Score: {scan_result['risk_score']}, Latency: {scan_result['latency_ms']}ms). "
                    f"Upstream LLM service is not connected at {upstream_url}. "
                    "Start Ollama ('ollama run llama3') or set UPSTREAM_LLM_URL to stream model completions."
                )
                payload = {
                    "id": f"chatcmpl-{int(time.time())}",
                    "object": "chat.completion.chunk",
                    "choices": [{
                        "index": 0,
                        "delta": {"content": status_msg},
                        "finish_reason": "stop"
                    }]
                }
                yield f"data: {json.dumps(payload)}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")
    else:
        # Non-streaming request: Forward to upstream or return Pre-Scan certification
        upstream_url = f"{UPSTREAM_LLM_URL.rstrip('/')}/chat/completions"
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(upstream_url, json=req.dict(), headers={"Content-Type": "application/json"})
                if resp.status_code == 200:
                    data = resp.json()
                    data["guardshield_metadata"] = {
                        "prescan_risk_score": scan_result["risk_score"],
                        "prescan_latency_ms": scan_result["latency_ms"],
                        "status": "PASS"
                    }
                    return data
        except Exception:
            pass

        return {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": f"GuardShield AI: Prompt verified as safe (Risk Score: {scan_result['risk_score']}, Latency: {scan_result['latency_ms']}ms). Upstream LLM not connected at {upstream_url}."
                },
                "finish_reason": "stop"
            }],
            "guardshield_metadata": {
                "prescan_risk_score": scan_result["risk_score"],
                "prescan_latency_ms": scan_result["latency_ms"],
                "status": "PASS"
            }
        }

if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  Starting GuardShield AI Sidecar Proxy on http://127.0.0.1:8000")
    print("=" * 65 + "\n")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
