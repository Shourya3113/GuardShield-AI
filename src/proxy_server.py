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
import re
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

# Regex Heuristics for Conversational Routing
PLEASANTRY_REGEX = re.compile(
    r"^[\s,\.!]*(ok|okay|sure|thanks|thank you|sounds good|cool|great|got it|proceed|continue|yes|no|understood|hello|hi|hey|bye|that helps|much appreciated|for the help)([\s,\.!]+(ok|okay|sure|thanks|thank you|sounds good|cool|great|got it|proceed|continue|yes|no|understood|hello|hi|hey|bye|that helps|much appreciated|for the help))*[\s,\.!]*$",
    re.IGNORECASE
)

HINGLISH_REGEX = re.compile(
    r"\b(kya|hai|hain|kaise|batao|bhai|mujhe|mera|meri|hum|aap|nahi|nahin|karna|karte|achha|theek|shukriya|dhanyawad|yaar|namaste|chalo|bolo|karo|raha|rahi|samajh|ye|wo|ki|ka|ke|ko|se|me|par)\b",
    re.IGNORECASE
)

ATTACK_KEYWORDS = re.compile(
    r"(ignore previous|bypass|jailbreak|override|system prompt|dan mode|unrestricted|developer mode)",
    re.IGNORECASE
)

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
    # Every ingress turn (system, user, assistant, tool) is validated.
    prev_context = ""
    routing_tags = []
    
    for idx, msg in enumerate(req.messages):
        content = msg.content.strip()
        if not content:
            continue
            
        role = msg.role.lower()
        
        # Scan system and tool messages
        if role in ("system", "tool"):
            sys_res = await asyncio.to_thread(prescan_filter.inspect_prompt, content)
            if not sys_res["is_safe"]:
                logger.warning(f"Ingress message #{idx+1} ({role}) blocked (Risk: {sys_res['risk_score']})")
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "error": {
                            "message": f"GuardShield AI: Ingress {role} message #{idx+1} blocked due to security policy violation.",
                            "type": "security_policy_violation",
                            "code": f"{role.upper()}_INJECTION_DETECTED",
                            "risk_score": sys_res["risk_score"],
                            "latency_ms": sys_res["latency_ms"]
                        }
                    }
                )
        elif role == "assistant":
            # Guard against forged assistant completions injecting jailbreak patterns
            if ATTACK_KEYWORDS.search(content):
                asst_res = await asyncio.to_thread(prescan_filter.inspect_prompt, content)
                if not asst_res["is_safe"]:
                    logger.warning(f"Forged assistant message #{idx+1} blocked (Risk: {asst_res['risk_score']})")
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content={
                            "error": {
                                "message": f"GuardShield AI: Ingress assistant message #{idx+1} blocked due to adversarial injection violation.",
                                "type": "security_policy_violation",
                                "code": "ASSISTANT_INJECTION_DETECTED",
                                "risk_score": asst_res["risk_score"],
                                "latency_ms": asst_res["latency_ms"]
                            }
                        }
                    )
            prev_context = content
        elif role == "user":
            # Check for conversational pleasantries / acknowledgements ("ok thanks, that helps", "proceed")
            is_pleasantry = bool(PLEASANTRY_REGEX.match(content)) and not bool(ATTACK_KEYWORDS.search(content))
            
            # Check for benign Hinglish / Hindi code-mixing
            is_hinglish = (bool(re.search(r"[\u0900-\u097F]", content)) or len(HINGLISH_REGEX.findall(content)) >= 2) and not bool(ATTACK_KEYWORDS.search(content))
            
            if is_pleasantry:
                logger.info(f"User message #{idx+1} matched conversational pleasantry pattern; passed.")
                prev_context = content
                continue
            elif is_hinglish:
                logger.info(f"User message #{idx+1} routed as benign multilingual/Hinglish traffic.")
                routing_tags.append("multilingual-hinglish-allowed")
                prev_context = content
                continue
                
            # For short conversational follow-ups (< 50 chars or <= 6 words), attach prior context
            if len(content) < 50 and len(content.split()) <= 6 and prev_context:
                scan_target = f"Context: {prev_context[-300:]}\nTurn: {content}"
            else:
                scan_target = content
                
            user_res = await asyncio.to_thread(prescan_filter.inspect_prompt, scan_target)
            logger.info(f"Turn #{idx+1} (user) Decision: {user_res['decision']} (Risk: {user_res['risk_score']}, Latency: {user_res['latency_ms']}ms)")
            
            if not user_res["is_safe"]:
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "error": {
                            "message": f"GuardShield AI: User message #{idx+1} blocked due to security policy violation (Adversarial Prompt Injection / Jailbreak detected).",
                            "type": "security_policy_violation",
                            "code": "PROMPT_INJECTION_DETECTED",
                            "risk_score": user_res["risk_score"],
                            "latency_ms": user_res["latency_ms"]
                        }
                    }
                )
            prev_context = content

    # 3. UPSTREAM LLM FORWARDING
    upstream_url = f"{UPSTREAM_LLM_URL.rstrip('/')}/chat/completions"
    req_payload = req.dict(exclude={"grounding_context"})

    if req.stream:
        # Pre-connect to upstream before sending 200 headers to prevent synthetic 200 on connection failure
        client = httpx.AsyncClient(timeout=60.0)
        try:
            upstream_req = client.build_request(
                "POST",
                upstream_url,
                json=req_payload,
                headers={"Content-Type": "application/json"}
            )
            resp = await client.send(upstream_req, stream=True)
            if resp.status_code != 200:
                err_body = await resp.aread()
                await resp.aclose()
                await client.aclose()
                return JSONResponse(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    content={
                        "error": {
                            "message": f"Upstream LLM service returned HTTP {resp.status_code}: {err_body.decode('utf-8', errors='ignore')}",
                            "type": "upstream_error",
                            "code": "BAD_GATEWAY"
                        }
                    }
                )
        except Exception as exc:
            await client.aclose()
            logger.error(f"Failed to connect to upstream LLM at {upstream_url}: {exc}")
            return JSONResponse(
                status_code=status.HTTP_502_BAD_GATEWAY,
                content={
                    "error": {
                        "message": f"GuardShield AI: Cannot reach upstream LLM service at {upstream_url}. Ensure upstream server (e.g. Ollama or vLLM) is running.",
                        "type": "upstream_error",
                        "code": "BAD_GATEWAY"
                    }
                }
            )

        async def event_generator():
            session_entropy_engine = StreamingEntropyEngine(spike_threshold=1.25, consecutive_spike_limit=2)
            try:
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
            finally:
                await resp.aclose()
                await client.aclose()

        headers = {}
        if routing_tags:
            headers["X-GuardShield-Routing"] = ",".join(routing_tags)
        return StreamingResponse(event_generator(), media_type="text/event-stream", headers=headers)
    else:
        # Non-streaming request: Forward to upstream and optionally apply Stage 2 fact grounding
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(upstream_url, json=req_payload, headers={"Content-Type": "application/json"})
                if resp.status_code == 200:
                    data = resp.json()
                    metadata = {
                        "status": "PASS",
                        "routing": routing_tags if routing_tags else "standard"
                    }
                    
                    # Stage 2 Fact Grounding verification if reference context is supplied
                    if req.grounding_context:
                        if nli_verifier is not None:
                            generated_msg = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                            if generated_msg:
                                nli_res = await asyncio.to_thread(nli_verifier.verify_claim, req.grounding_context, generated_msg)
                                metadata["stage2_factuality"] = {
                                    "decision": nli_res.get("decision"),
                                    "is_hallucination": nli_res.get("is_hallucination"),
                                    "is_contradiction": nli_res.get("is_contradiction", False),
                                    "is_unverified": nli_res.get("is_unverified", False),
                                    "contradiction_prob": nli_res.get("contradiction_prob"),
                                    "entailment_prob": nli_res.get("entailment_prob"),
                                    "neutral_prob": nli_res.get("neutral_prob"),
                                    "latency_ms": nli_res.get("latency_ms")
                                }
                        else:
                            logger.warning("Stage 2 grounding requested, but NLI verifier is not loaded.")
                            metadata["stage2_factuality"] = {
                                "status": "UNAVAILABLE",
                                "warning": "Stage 2 NLI verifier model is not loaded in current environment; fact grounding skipped."
                            }
                            
                    data["guardshield_metadata"] = metadata
                    response = JSONResponse(content=data)
                    if routing_tags:
                        response.headers["X-GuardShield-Routing"] = ",".join(routing_tags)
                    return response
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
