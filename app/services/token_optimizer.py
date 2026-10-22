"""
Token Optimizer & LLM Execution Guardrail for FieldForesight

Features:
1. LLM_MODE control:
   - 'live': Real Groq API calls (strictly capped at MAX_LIVE_CALLS per run)
   - 'replay': Pre-saved high-quality responses from tests/fixtures/llm_responses/
   - 'dry_run': Zero API calls; calculates prompt size and logs token estimation
2. Exact Response Cache:
   - Hashes model + system_prompt + user_prompt using SHA-256
   - Reusable across sessions to eliminate redundant Groq invocations
3. Live Call Budget Enforcer:
   - Maximum 5 live calls per run by default
   - Shows remaining call budget before each live call
   - Throws RuntimeError if live budget exceeded
4. Token Usage Tracker:
   - Differentiates live vs replay calls with `is_live` field
   - Generates audit reports separating real API tokens from simulated/replayed tokens
5. Cheap-Model Routing:
   - Routes simple queries/greetings to lighter model (llama-3.1-8b-instant)
   - Reserves heavy 70B model (llama-3.3-70b-versatile) for complex multi-factor synthesis

Groq Cloud Free Tier Rate Limits (Configurable, not hardcoded):
- Requests Per Minute (RPM): 30
- Requests Per Day (RPD): 14,400
- Tokens Per Minute (TPM): 6,000 (70B) / 20,000 (8B)
- Tokens Per Day (TPD): 500,000
"""

import os
import json
import time
import hashlib
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"
RESPONSES_FILE = FIXTURES_DIR / "llm_responses" / "responses.json"
CACHE_FILE = REPO_ROOT / "app" / "data" / "llm_cache.json"

# ==========================================
# 1. Configuration & Groq Rate Limits
# ==========================================
# Groq Free Tier Limits (Read from environment, defaults to official tier specs)
GROQ_FREE_RPM = int(os.getenv("GROQ_FREE_RPM", "30"))
GROQ_FREE_RPD = int(os.getenv("GROQ_FREE_RPD", "14400"))
GROQ_FREE_TPM_70B = int(os.getenv("GROQ_FREE_TPM_70B", "6000"))
GROQ_FREE_TPM_8B = int(os.getenv("GROQ_FREE_TPM_8B", "20000"))
GROQ_FREE_TPD = int(os.getenv("GROQ_FREE_TPD", "500000"))

# LLM execution mode: 'live' | 'replay' | 'dry_run' (Default: replay)
LLM_MODE = os.getenv("LLM_MODE", "replay").strip().lower()

# Maximum permitted live calls per process run
MAX_LIVE_CALLS = int(os.getenv("MAX_LIVE_CALLS", "5"))

# In-memory session trackers
_live_call_lock = threading.Lock()
_live_call_count = 0
_usage_logs: List[Dict[str, Any]] = []
_memory_cache: Dict[str, Dict[str, Any]] = {}


def get_current_mode() -> str:
    """Returns current active LLM mode ('live', 'replay', or 'dry_run')."""
    return os.getenv("LLM_MODE", LLM_MODE).strip().lower()


def set_mode(mode: str) -> None:
    """Sets the LLM mode dynamically for tests or scripts."""
    global LLM_MODE
    valid_modes = {"live", "replay", "dry_run"}
    if mode.lower() not in valid_modes:
        raise ValueError(f"Invalid mode '{mode}'. Choose from {valid_modes}")
    LLM_MODE = mode.lower()
    os.environ["LLM_MODE"] = LLM_MODE


def reset_live_counter() -> None:
    """Resets the live call counter for a new test suite or session."""
    global _live_call_count, _usage_logs
    with _live_call_lock:
        _live_call_count = 0
        _usage_logs = []


# ==========================================
# 2. Token Estimation
# ==========================================
def estimate_tokens(text: str) -> int:
    """
    Accurately estimates token count for multilingual English/Bangla text.
    In SentencePiece/Byte-Pair Encoding:
      - English averages ~4.0 characters per token
      - Bengali averages ~2.6 characters per token due to multi-byte unicode subwords
    """
    if not text:
        return 0
    bangla_chars = sum(1 for c in text if '\u0980' <= c <= '\u09FF')
    ascii_chars = len(text) - bangla_chars

    tokens_bangla = bangla_chars / 2.6
    tokens_ascii = ascii_chars / 4.0
    return max(1, int(round(tokens_bangla + tokens_ascii)))


# ==========================================
# 3. Cache Management
# ==========================================
def _compute_hash(model: str, messages: List[Dict[str, str]]) -> str:
    serialized = f"{model}::" + json.dumps(messages, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _load_disk_cache() -> Dict[str, Any]:
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_disk_cache(cache: Dict[str, Any]) -> None:
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def get_cached_response(model: str, messages: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
    key = _compute_hash(model, messages)
    if key in _memory_cache:
        return _memory_cache[key]
    disk_cache = _load_disk_cache()
    if key in disk_cache:
        _memory_cache[key] = disk_cache[key]
        return disk_cache[key]
    return None


def store_cached_response(model: str, messages: List[Dict[str, str]], content: str) -> None:
    key = _compute_hash(model, messages)
    data = {
        "content": content,
        "model": model,
        "timestamp": time.time(),
    }
    _memory_cache[key] = data
    disk_cache = _load_disk_cache()
    disk_cache[key] = data
    _save_disk_cache(disk_cache)


# ==========================================
# 4. Live Call Guardrail
# ==========================================
def register_live_call_intent(model: str) -> int:
    """
    Validates live call budget. Increments counter and prints remaining allowance.
    Raises RuntimeError if maximum live call quota is exceeded.
    """
    global _live_call_count
    with _live_call_lock:
        if _live_call_count >= MAX_LIVE_CALLS:
            raise RuntimeError(
                f"🚨 Live Groq call budget exceeded! Maximum {MAX_LIVE_CALLS} live calls "
                f"allowed per run to protect rate limits and prevent API exhaustion. "
                f"Current live calls: {_live_call_count}."
            )
        _live_call_count += 1
        remaining = MAX_LIVE_CALLS - _live_call_count
        print(
            f"⚡ [TokenOptimizer] LIVE Groq API call initiating ({model})... "
            f"Live call #{_live_call_count} (Remaining live budget: {remaining})"
        )
        return _live_call_count


# ==========================================
# 5. Replay Provider
# ==========================================
def get_replay_response(query_id: Optional[str] = None, prompt_text: str = "") -> Optional[Dict[str, Any]]:
    """
    Retrieves grounded agronomic response from pre-saved fixtures in tests/fixtures/llm_responses/
    """
    if not RESPONSES_FILE.exists():
        return None

    try:
        with open(RESPONSES_FILE, "r", encoding="utf-8") as f:
            fixtures = json.load(f)

        if query_id and query_id in fixtures:
            return fixtures[query_id]

        # Fuzzy match by key topic or crop keywords if query_id is not given
        text_lower = prompt_text.lower()
        if any(w in text_lower for w in ["কীটনাশক", "বালাইনাশক", "ছত্রাকনাশক", "মিলি", "মাত্রা", "pesticide", "dosage"]):
            return fixtures.get("chat-02")
        if "নাবি ধসা" in text_lower or "late blight" in text_lower:
            return fixtures.get("chat-02")
        if ("গম" in text_lower and "সেচ" in text_lower) or "সিআরআই" in text_lower or "cri" in text_lower:
            return fixtures.get("chat-03")
        if "সেচ" in text_lower or "awd" in text_lower:
            return fixtures.get("chat-01")
        if "আর্মিওয়ার্ম" in text_lower or "armyworm" in text_lower:
            return fixtures.get("chat-04")
        if "জাবপোকা" in text_lower or "aphid" in text_lower:
            return fixtures.get("chat-05")
        if "লবণাক্ত" in text_lower or "salin" in text_lower:
            return fixtures.get("chat-08")
        if "হাওর" in text_lower or "ঢল" in text_lower:
            return fixtures.get("chat-09")
        if "ব্লাস্ট" in text_lower or "blast" in text_lower:
            return fixtures.get("chat-13")

        # Fallback to chat-01 for general query
        return fixtures.get("chat-01")
    except Exception:
        return None


# ==========================================
# 6. Cheap-Model Routing
# ==========================================
def route_model(prompt: str, requested_model: str = "llama-3.3-70b-versatile") -> str:
    """
    Intelligently routes simpler queries to llama-3.1-8b-instant (lighter, 3x faster, 3x higher TPM limit).
    Reserves llama-3.3-70b-versatile for complex multi-factor risk synthesis.
    """
    simple_greetings = {"সালাম", "hello", "hi", "কেমন আছেন", "নমস্কার", "ধন্যবাদ", "thanks"}
    prompt_clean = prompt.strip().lower()

    # Short greetings or single-word queries
    if len(prompt_clean) < 30 and any(g in prompt_clean for g in simple_greetings):
        return "llama-3.1-8b-instant"

    # Quick scope checking or definition queries
    if len(prompt_clean) < 50 and ("কী" in prompt_clean or "what is" in prompt_clean):
        return "llama-3.1-8b-instant"

    return requested_model


# ==========================================
# 7. Usage Logging & Audit Reporting
# ==========================================
def log_token_usage(
    mode: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    cached: bool = False,
    is_live: bool = False,
    latency_ms: float = 0.0,
    query_id: Optional[str] = None,
    is_estimated: bool = False,
) -> None:
    """
    Appends an audit record distinguishing live calls from replay/dry_run calls.
    """
    total_tokens = prompt_tokens + completion_tokens
    record = {
        "timestamp": time.time(),
        "mode": mode,
        "is_live": is_live,
        "cached": cached,
        "model": model,
        "query_id": query_id,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "latency_ms": round(latency_ms, 2),
        "is_estimated": is_estimated,
    }
    _usage_logs.append(record)


def get_token_usage_summary() -> Dict[str, Any]:
    """
    Aggregates full token metrics across the run:
    - Number of live calls
    - Number of replay / dry_run calls
    - Tokens consumed vs tokens saved via cache & replay
    """
    live_calls = sum(1 for r in _usage_logs if r["is_live"])
    replay_calls = sum(1 for r in _usage_logs if r["mode"] == "replay" and not r["cached"])
    dry_run_calls = sum(1 for r in _usage_logs if r["mode"] == "dry_run")
    cache_hits = sum(1 for r in _usage_logs if r["cached"])

    live_tokens = sum(r["total_tokens"] for r in _usage_logs if r["is_live"])
    saved_tokens = sum(r["total_tokens"] for r in _usage_logs if not r["is_live"] or r["cached"])
    total_prompt_tokens = sum(r["prompt_tokens"] for r in _usage_logs)
    total_completion_tokens = sum(r["completion_tokens"] for r in _usage_logs)

    return {
        "active_mode": get_current_mode(),
        "total_calls": len(_usage_logs),
        "live_calls_count": live_calls,
        "replay_calls_count": replay_calls,
        "dry_run_calls_count": dry_run_calls,
        "cache_hits_count": cache_hits,
        "live_tokens_consumed": live_tokens,
        "tokens_saved_by_cache_and_replay": saved_tokens,
        "total_prompt_tokens": total_prompt_tokens,
        "total_completion_tokens": total_completion_tokens,
        "total_tokens_accounted": total_prompt_tokens + total_completion_tokens,
        "max_live_budget": MAX_LIVE_CALLS,
        "remaining_live_budget": max(0, MAX_LIVE_CALLS - live_calls),
    }
