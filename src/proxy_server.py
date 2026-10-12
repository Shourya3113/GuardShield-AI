import os
import sys
import time
import math
import json
import asyncio
import logging
from pathlib import Path
from collections import OrderedDict
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any, Union, Callable
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, ConfigDict, Field
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
import hmac
import hashlib
import secrets

# Upstream LLM Service (e.g. Ollama, vLLM, or local OpenAI-compatible endpoint)
UPSTREAM_LLM_URL = os.environ.get("UPSTREAM_LLM_URL", "http://localhost:11434/v1")

# Safety Caps
MAX_INPUT_CHARS = int(os.environ.get("GUARDSHIELD_MAX_INPUT_CHARS", "32768"))

# Short turns are additionally scanned together with the preceding turn (see scan_messages).
SHORT_TURN_MAX_CHARS = 50
SHORT_TURN_MAX_WORDS = 6
CONTEXT_WINDOW_CHARS = 300

# Cryptographic Assistant History Signing
# The proxy signs authentic assistant turns it relays from the upstream LLM.
# On re-submission in multi-turn dialogues, signed assistant turns are recognized as trusted history
# and exempt from Stage 1 scanning, while unsigned or forged assistant turns are scanned unconditionally.
# The key must never be a public constant: anyone who knows it can forge "trusted" assistant turns and
# skip Stage 1. Without GUARDSHIELD_PROXY_SECRET an ephemeral per-process key is generated, so client-held
# signatures stop verifying after a restart (re-submitted turns are then simply scanned).
_ENV_SECRET = os.environ.get("GUARDSHIELD_PROXY_SECRET")
if _ENV_SECRET:
    PROXY_SECRET_KEY = _ENV_SECRET.encode("utf-8")
    SIGNING_KEY_SOURCE = "environment"
else:
    PROXY_SECRET_KEY = secrets.token_bytes(32)
    SIGNING_KEY_SOURCE = "ephemeral"
    logger.warning("GUARDSHIELD_PROXY_SECRET is not set; using an ephemeral per-process assistant signing key.")

MAX_SIGNATURE_CACHE = 50000
RELAYED_SIGNATURE_CACHE: "OrderedDict[str, None]" = OrderedDict()

def compute_assistant_signature(content: str) -> str:
    """Computes HMAC-SHA256 signature for trusted assistant messages generated/relayed by the proxy."""
    return hmac.new(PROXY_SECRET_KEY, content.strip().encode("utf-8"), hashlib.sha256).hexdigest()

def verify_assistant_signature(content: str, provided_signature: Optional[str] = None) -> bool:
    """Verifies whether an assistant message was authentically generated and relayed by GuardShield proxy."""
    expected_sig = compute_assistant_signature(content)
    if expected_sig in RELAYED_SIGNATURE_CACHE:
        return True
    if provided_signature and hmac.compare_digest(expected_sig, provided_signature):
        return True
    return False

def record_assistant_signature(content: str) -> str:
    """Records generated assistant text into the trusted signature cache (oldest entries evicted first)."""
    sig = compute_assistant_signature(content)
    RELAYED_SIGNATURE_CACHE[sig] = None
    RELAYED_SIGNATURE_CACHE.move_to_end(sig)
    while len(RELAYED_SIGNATURE_CACHE) > MAX_SIGNATURE_CACHE:
        RELAYED_SIGNATURE_CACHE.popitem(last=False)
    return sig

def message_text(content: Union[str, List[Dict[str, Any]], None]) -> str:
    """Flattens OpenAI-style message content (string, list of content parts, or null) into scannable text."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    return "\n".join(
        part["text"] for part in content
        if isinstance(part, dict) and isinstance(part.get("text"), str)
    )

def scan_messages(
    engine,
    messages: List[Dict[str, Any]],
    verify_signature: Optional[Callable[[str, Optional[str]], bool]] = None,
    stop_on_block: bool = True,
) -> Dict[str, Any]:
    """
    Runs Stage 1 over every turn of a conversation, stopping at the first blocked turn
    (stop_on_block=False scores every turn, for benchmarking).
    `messages` are dicts with 'role', 'content' and optional 'proxy_signature' / 'signature'.

    - User, system, tool and unsigned/forged assistant turns are always scanned on their own text.
    - Short turns are additionally scanned together with the preceding scanned turn and the higher risk
      wins (catches attacks split across turns), so context can only add risk, never dilute a short
      attack below threshold.
    - Assistant turns carrying a valid proxy signature are trusted history: they are neither scanned
      nor used as context for the next turn.
    """
    verify_signature = verify_signature or verify_assistant_signature
    prev_context = ""
    turns = []
    blocked = None
    for idx, msg in enumerate(messages):
        content = message_text(msg.get("content")).strip()
        if not content:
            continue
        role = str(msg.get("role", "")).lower()

        # Assistant turn verification (Signed History vs. Untrusted/Forged Turn)
        if role == "assistant":
            provided_sig = msg.get("proxy_signature") or msg.get("signature")
            if verify_signature(content, provided_sig):
                logger.info(f"Turn #{idx+1} (assistant): VERIFIED SIGNED HISTORY (Skipping Stage 1 scan).")
                turns.append({"index": idx, "role": role, "signed": True, "risk_score": None, "is_safe": True})
                prev_context = ""
                continue
            logger.warning(f"Turn #{idx+1} (assistant): UNSIGNED / FORGED ASSISTANT TURN -> Subject to unconditional Stage 1 neural scan.")

        res = engine.inspect_prompt(content)
        risk, latency = res["risk_score"], res["latency_ms"]
        if len(content) < SHORT_TURN_MAX_CHARS and len(content.split()) <= SHORT_TURN_MAX_WORDS and prev_context:
            ctx_res = engine.inspect_prompt(f"Context: {prev_context[-CONTEXT_WINDOW_CHARS:]}\nTurn: {content}")
            risk = max(risk, ctx_res["risk_score"])
            latency = round(latency + ctx_res["latency_ms"], 2)

        is_safe = risk < engine.threshold
        logger.info(f"Turn #{idx+1} ({role}) Decision: {'ALLOW' if is_safe else 'BLOCK'} (Risk: {risk}, Latency: {latency}ms)")
        turns.append({"index": idx, "role": role, "signed": False, "risk_score": risk, "is_safe": is_safe, "latency_ms": latency})
        if not is_safe and blocked is None:
            blocked = {"blocked": True, "turn_index": idx, "role": role, "risk_score": risk, "latency_ms": latency}
            if stop_on_block:
                break
        prev_context = content

    return dict(blocked or {"blocked": False}, turns=turns)

# Pydantic Schemas for OpenAI / Ollama Compatibility
class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="allow")  # pass through name, tool_calls, tool_call_id, ...
    role: str
    content: Optional[Union[str, List[Dict[str, Any]]]] = None
    proxy_signature: Optional[str] = Field(default=None, description="HMAC-SHA256 signature for verified relayed assistant turns.")
    signature: Optional[str] = Field(default=None, description="Alias for proxy_signature.")

class ChatCompletionRequest(BaseModel):
    model_config = ConfigDict(extra="allow")  # pass through max_tokens, stop, tools, ...
    model: Optional[str] = "llama3.1:8b"
    messages: List[ChatMessage]
    stream: Optional[bool] = False
    temperature: Optional[float] = 0.7
    logprobs: Optional[bool] = True
    top_logprobs: Optional[int] = 3
    grounding_context: Optional[str] = Field(default=None, description="Optional authoritative reference text for Stage 2 fact verification.")

def build_upstream_payload(req: ChatCompletionRequest) -> Dict[str, Any]:
    """Serializes the request for the upstream LLM without proxy-only fields, which strict OpenAI-compatible servers reject."""
    payload = req.model_dump(exclude={"grounding_context"})
    for m in payload["messages"]:
        m.pop("proxy_signature", None)
        m.pop("signature", None)
    return payload

def first_choice_message(data: Any) -> Optional[Dict[str, Any]]:
    choices = data.get("choices") if isinstance(data, dict) else None
    if not choices or not isinstance(choices[0], dict):
        return None
    msg = choices[0].get("message")
    return msg if isinstance(msg, dict) else None

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
    version="1.2.0",
    lifespan=lifespan
)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "GuardShield AI Sidecar Proxy",
        "pipeline": "Stage 1 (Pre-Scan DeBERTa-v3) -> Stage 2 (Windowed NLI Verifier)",
        "assistant_signing_enabled": True,
        "assistant_signing_key": SIGNING_KEY_SOURCE,
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
    total_chars = sum(len(message_text(m.content)) for m in req.messages)
    if total_chars > MAX_INPUT_CHARS:
        raise HTTPException(
            status_code=413,
            detail=f"Request payload ({total_chars:,} chars) exceeds the safety cap of {MAX_INPUT_CHARS:,} characters."
        )

    # 2. MULTI-TURN SCANNING WITH CRYPTOGRAPHIC ASSISTANT SIGNING (see scan_messages)
    scan = await asyncio.to_thread(scan_messages, prescan_filter, [m.model_dump() for m in req.messages])
    if scan["blocked"]:
        idx, role = scan["turn_index"], scan["role"]
        logger.warning(f"Ingress message #{idx+1} ({role}) blocked (Risk: {scan['risk_score']})")
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error": {
                    "message": f"GuardShield AI: Ingress {role} message #{idx+1} blocked due to security policy violation.",
                    "type": "security_policy_violation",
                    "code": f"{role.upper()}_INJECTION_DETECTED",
                    "risk_score": scan["risk_score"],
                    "latency_ms": scan["latency_ms"]
                }
            }
        )

    # 3. UPSTREAM LLM FORWARDING
    upstream_url = f"{UPSTREAM_LLM_URL.rstrip('/')}/chat/completions"
    req_payload = build_upstream_payload(req)

    if req.stream:
        if req.grounding_context:
            logger.warning("grounding_context is ignored for streaming requests; Stage 2 runs on non-streaming responses only.")
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

        streamed_chunks_accum = []
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

                            if content_chunk:
                                streamed_chunks_accum.append(content_chunk)
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
                if streamed_chunks_accum:
                    full_text = "".join(streamed_chunks_accum)
                    record_assistant_signature(full_text)
                await resp.aclose()
                await client.aclose()

        return StreamingResponse(event_generator(), media_type="text/event-stream")
    else:
        # Non-streaming request: Forward to upstream and optionally apply Stage 2 fact grounding
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(upstream_url, json=req_payload, headers={"Content-Type": "application/json"})
                if resp.status_code == 200:
                    data = resp.json()
                    metadata = {
                        "status": "PASS",
                        "routing": "neural_prescan"
                    }

                    # Cryptographically sign the assistant response
                    assistant_msg = first_choice_message(data)
                    generated_msg = message_text(assistant_msg.get("content")) if assistant_msg else ""
                    if generated_msg:
                        asst_sig = record_assistant_signature(generated_msg)
                        assistant_msg["proxy_signature"] = asst_sig
                        assistant_msg["signature"] = asst_sig
                        metadata["assistant_signature"] = asst_sig

                    # Stage 2 Fact Grounding verification if reference context is supplied
                    if req.grounding_context:
                        if nli_verifier is not None:
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
                    headers = {}
                    if "assistant_signature" in metadata:
                        headers["X-GuardShield-Assistant-Signature"] = metadata["assistant_signature"]
                    return JSONResponse(content=data, headers=headers)
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
