import os
import sys
import time
import json
import logging
from pathlib import Path
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

# Pydantic Schemas for OpenAI / Ollama Compatibility
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: Optional[str] = "llama3.1:8b"
    messages: List[ChatMessage]
    stream: Optional[bool] = False
    temperature: Optional[float] = 0.7

app = FastAPI(
    title="GuardShield AI — Real-Time Sidecar Proxy",
    description="Dual-stage sidecar proxy for prompt injection defense & real-time streaming hallucination detection.",
    version="1.0.0"
)

# Global Filter Engines
prescan_filter: Optional[PreScanSecurityFilter] = None
entropy_engine = StreamingEntropyEngine(spike_threshold=1.20, consecutive_spike_limit=2)

@app.on_event("startup")
def load_security_engines():
    global prescan_filter
    logger.info("Initializing GuardShield Pre-Scan Security Filter...")
    prescan_filter = PreScanSecurityFilter()
    logger.info("GuardShield Sidecar Proxy Server initialized successfully.")

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
            entropy_engine.reset()
            # Simulated factual response chunks
            chunks = ["GuardShield", " AI", " sidecar", " proxy", " successfully", " verified", " user", " query."]
            for chunk in chunks:
                # Simulated high-confidence token probabilities
                res = entropy_engine.process_token(chunk, [0.95, 0.03, 0.02])
                payload = {
                    "id": f"chatcmpl-{int(time.time())}",
                    "object": "chat.completion.chunk",
                    "created": int(time.time()),
                    "choices": [{
                        "index": 0,
                        "delta": {"content": chunk},
                        "entropy": res["entropy"],
                        "status": res["status"]
                    }]
                }
                yield f"data: {json.dumps(payload)}\n\n"
                time.sleep(0.02)
            yield "data: [DONE]\n\n"
            
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    else:
        return {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "GuardShield AI sidecar proxy successfully processed your secure prompt."
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
