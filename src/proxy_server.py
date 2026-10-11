import os
import sys
import time
import math
import json
import asyncio
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
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
from nli_verifier import WindowedNLIVerifier

import httpx

# Upstream LLM Service (e.g. Ollama, vLLM, or local OpenAI-compatible endpoint)
UPSTREAM_LLM_URL = os.environ.get("UPSTREAM_LLM_URL", "http://localhost:11434/v1")

# Safety Caps
MAX_INPUT_CHARS = int(os.environ.get("GUARDSHIELD_MAX_INPUT_CHARS", "32768"))

# Pydantic Schemas for OpenAI / Ollama Compatibility
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: Optional[str] = "llama3.1:8b"
    messages: List[ChatMessage]
    stream: Optional[bool] = False
    temperature: Optional[float] = 0.7
    logprobs: Optional[bool] = True
    top_logprobs: Optional[int] = 3
    grounding_context: Optional[str] = Field(default=None, description="Optional authoritative reference text for Stage 2 fact verification.")

# Global Models (loaded once on startup)
prescan_filter: Optional[PreScanSecurityFilter] = None
nli_verifier: Optional[WindowedNLIVerifier] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global prescan_filter, nli_verifier
    logger.info("Initializing GuardShield Pre-Scan Security Filter...")
    allow_fallback = os.environ.get("GUARDSHIELD_ALLOW_UNTRAINED_FALLBACK", "0") == "1"
    prescan_filter = PreScanSecurityFilter(allow_untrained_fallback=allow_fallback)
    
    try:
        nli_verifier = WindowedNLIVerifier()
        logger.info("GuardShield Stage 2 NLI Fact Grounder initialized.")
    except Exception as e:
        logger.warning(f"Stage 2 NLI Verifier offline or unavailable ({e}); Stage 1 active.")
        
    logger.info("GuardShield Sidecar Proxy Server initialized successfully.")
    yield

app = FastAPI(
    title="GuardShield AI — Real-Time Sidecar Proxy",
    description="Dual-stage sidecar proxy for prompt injection defense & real-time streaming hallucination detection.",
    version="1.1.0",
    lifespan=lifespan
)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "GuardShield AI Sidecar Proxy",
        "target_latency": "< 25ms",
        "prescan_ready": prescan_filter is not None,
        "nli_grounder_ready": nli_verifier is not None,
        "max_input_chars": MAX_INPUT_CHARS
    }

@app.post("/v1/chat/completions")
async def chat_completions(req: ChatCompletionRequest):
    global prescan_filter, nli_verifier
    if not prescan_filter:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Security Filter initializing...")
        
    # 1. INPUT LENGTH CAP (Mitigating DoS / Memory Exhaustion)
    total_chars = sum(len(m.content) for m in req.messages)
    if total_chars > MAX_INPUT_CHARS:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Request payload ({total_chars:,} chars) exceeds the safety cap of {MAX_INPUT_CHARS:,} characters."
        )

    # 2. MULTI-TURN & ROLE-AWARE SCANNING
    # Inspects system, tool, and user messages. For short user turns (< 20 chars or <= 3 words),
    # attaches prior turn context so the classifier does not trigger on zero-context continuation tokens.
    scan_target = ""
    prev_user_or_asst = ""
    
    for msg in req.messages:
        content = msg.content.strip()
        if not content:
            continue
            
        if msg.role in ("system", "tool"):
            # Asynchronous scan of system/tool message
            sys_res = await asyncio.to_thread(prescan_filter.inspect_prompt, content)
            if not sys_res["is_safe"]:
                logger.warning(f"Ingress {msg.role.upper()} message blocked (Risk: {sys_res['risk_score']})")
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "error": {
                            "message": f"GuardShield AI: Ingress {msg.role.capitalize()} message blocked due to security policy violation.",
                            "type": "security_policy_violation",
                            "code": f"{msg.role.upper()}_INJECTION_DETECTED",
                            "risk_score": sys_res["risk_score"],
                            "latency_ms": sys_res["latency_ms"]
                        }
                    }
                )
        elif msg.role == "user":
            # Context-aware augmentation for short conversational turn ("continue", "ok thanks")
            if len(content) < 20 and len(content.split()) <= 3 and prev_user_or_asst:
                scan_target = f"Context: {prev_user_or_asst[-300:]}\nTurn: {content}"
            else:
                scan_target = content
            prev_user_or_asst = content
        elif msg.role == "assistant":
            prev_user_or_asst = content

    if not scan_target:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No user message provided.")

    # 3. STAGE 1: ASYNCHRONOUS PRE-SCAN SECURITY FILTER
    scan_result = await asyncio.to_thread(prescan_filter.inspect_prompt, scan_target)
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
        
    # 4. STAGE 2: LLM RESPONSE STREAMING & ENTROPY INSPECTION
    upstream_url = f"{UPSTREAM_LLM_URL.rstrip('/')}/chat/completions"
    
    if req.stream:
        # Pre-check upstream connectivity to prevent returning fake HTTP 200 on connection failure
        async def event_generator():
            session_entropy_engine = StreamingEntropyEngine(spike_threshold=1.25, consecutive_spike_limit=2)
            try:
                # Forward request payload excluding internal GuardShield fields
                req_payload = req.dict(exclude={"grounding_context"})
                async with httpx.AsyncClient(timeout=60.0) as client:
                    async with client.stream(
                        "POST",
                        upstream_url,
                        json=req_payload,
                        headers={"Content-Type": "application/json"}
                    ) as resp:
                        if resp.status_code != 200:
                            err_body = await resp.aread()
                            err_chunk = {
                                "error": {
                                    "message": f"Upstream LLM service returned HTTP {resp.status_code}: {err_body.decode('utf-8', errors='ignore')}",
                                    "type": "upstream_error",
                                    "code": "BAD_GATEWAY"
                                }
                            }
                            yield f"data: {json.dumps(err_chunk)}\n\n"
                            yield "data: [DONE]\n\n"
                            return

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
                                        choice_obj = chunk_json.get("choices", [{}])[0]
                                        extracted_probs = []

                                        logprobs_info = choice_obj.get("logprobs") or {}
                                        content_lps = logprobs_info.get("content") or []
                                        if content_lps and isinstance(content_lps, list):
                                            top_lps = content_lps[0].get("top_logprobs") or []
                                            for item in top_lps:
                                                if isinstance(item, dict) and "logprob" in item:
                                                    extracted_probs.append(math.exp(float(item["logprob"])))
                                        elif "top_logprobs" in logprobs_info and isinstance(logprobs_info["top_logprobs"], list):
                                            for item in logprobs_info["top_logprobs"]:
                                                if isinstance(item, dict) and "logprob" in item:
                                                    extracted_probs.append(math.exp(float(item["logprob"])))

                                        if len(extracted_probs) >= 2:
                                            res = session_entropy_engine.process_token(content_chunk, extracted_probs)
                                            choice_obj["entropy"] = res["entropy"]
                                            choice_obj["status"] = res["status"]

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
                                        else:
                                            choice_obj["entropy"] = None
                                            choice_obj["status"] = "PASSTHROUGH (Logprobs unavailable from upstream)"

                                    yield f"data: {json.dumps(chunk_json)}\n\n"
                                except Exception:
                                    yield f"{line}\n\n"
            except Exception as e:
                logger.error(f"Upstream streaming error at {upstream_url}: {e}")
                err_chunk = {
                    "error": {
                        "message": f"Upstream LLM service unreachable at {upstream_url}: {str(e)}",
                        "type": "upstream_error",
                        "code": "BAD_GATEWAY"
                    }
                }
                yield f"data: {json.dumps(err_chunk)}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")
    else:
        # Non-streaming request: Forward to upstream and optionally apply Stage 2 fact grounding
        req_payload = req.dict(exclude={"grounding_context"})
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(upstream_url, json=req_payload, headers={"Content-Type": "application/json"})
                if resp.status_code == 200:
                    data = resp.json()
                    metadata = {
                        "prescan_risk_score": scan_result["risk_score"],
                        "prescan_latency_ms": scan_result["latency_ms"],
                        "status": "PASS"
                    }
                    
                    # Stage 2 Fact Grounding verification if reference context is supplied
                    if req.grounding_context and nli_verifier is not None:
                        generated_msg = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                        if generated_msg:
                            nli_res = await asyncio.to_thread(nli_verifier.verify_claim, req.grounding_context, generated_msg)
                            metadata["stage2_factuality"] = {
                                "decision": nli_res.get("decision"),
                                "is_hallucination": nli_res.get("is_hallucination"),
                                "contradiction_prob": nli_res.get("contradiction_prob"),
                                "entailment_prob": nli_res.get("entailment_prob"),
                                "latency_ms": nli_res.get("latency_ms")
                            }
                            
                    data["guardshield_metadata"] = metadata
                    return data
                else:
                    return JSONResponse(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        content={
                            "error": {
                                "message": f"Upstream LLM service returned HTTP {resp.status_code}",
                                "type": "upstream_error",
                                "code": "BAD_GATEWAY"
                            }
                        }
                    )
        except Exception as e:
            logger.error(f"Upstream connection failed: {e}")
            return JSONResponse(
                status_code=status.HTTP_502_BAD_GATEWAY,
                content={
                    "error": {
                        "message": f"Upstream LLM service unreachable at {upstream_url}: {str(e)}",
                        "type": "upstream_error",
                        "code": "BAD_GATEWAY"
                    }
                }
            )

if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  Starting GuardShield AI Sidecar Proxy on http://127.0.0.1:8000")
    print("=" * 65 + "\n")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
