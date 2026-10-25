"""
Agricultural Chat Service: Guardrailed RAG Assistant for FieldForesight
Integrates:
  1. Scope verification (agriculture & platform topics only)
  2. Grounded RAG retrieval via ChromaDB knowledge vector store
  3. Strict pesticide dosage & chemical safety guardrails
  4. Groq LLM (llama-3.3-70b-versatile / qwen) with local grounded fallback
"""

import os
import time
import uuid
import re
import requests
from typing import Any, Dict, List, Optional, Union
from dotenv import load_dotenv

from app.services.rag_service import retrieve
from app.schemas.chat import ChatRequest, ChatResponse, ChatContextPayload, ChatHistoryItem
from app.services.token_optimizer import (
    get_current_mode,
    get_cached_response,
    store_cached_response,
    register_live_call_intent,
    get_replay_response,
    estimate_tokens,
    log_token_usage,
    route_model,
)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "llama-3.3-70b-versatile"
FALLBACK_MODEL = "llama-3.1-8b-instant"

# Common greetings
GREETING_PATTERNS = [
    r"^(hi|hello|hey|hola|greetings)\b",
    r"^(সালাম|আসসালামু\s*আলাইকুম|নমস্কার|আদাব|কেমন\s*আছেন|হ্যালো|হাই)\b",
]

# Agriculture & platform keywords in Bangla and English
AGRI_KEYWORDS = [
    "ধান", "গম", "ভুট্টা", "আলু", "সরিষা", "মসুর", "পাট", "ফসল", "চাষ", "সেচ", "সার", "ইউরিয়া",
    "কীটনাশক", "বালাই", "পোকামাকড়", "ব্লাস্ট", "ধসা", "ফলন", "মাটি", "বীজ", "আবহাওয়া", "বৃষ্টি",
    "খরা", "বন্যা", "জমি", "ক্ষেত", "রোগ", "ডোজ", "কৃষি", "মাঠ", "এনডিভিআই", "রংপুর", "দিনাজপুর",
    "ঢাকা", "বগুড়া", "মুন্সীগঞ্জ", "পাবনা", "সিরাজগঞ্জ", "fieldforesight", "ndvi", "crop",
    "yield", "rice", "wheat", "maize", "potato", "mustard", "lentil", "jute", "fertilizer",
    "irrigation", "pest", "disease", "seed", "weather", "soil", "harvest", "advisory", "risk"
]


def _is_greeting(text: str) -> bool:
    t = text.strip().lower()
    return any(re.search(pat, t) for pat in GREETING_PATTERNS) and len(t.split()) <= 4


def _is_agri_scope(text: str) -> bool:
    t = text.lower()
    return any(kw in t for kw in AGRI_KEYWORDS)


def _get_groq_api_key() -> str:
    load_dotenv(override=True)
    return os.getenv("GROQ_API_KEY", "").strip()


class PreparedContext(dict):
    """
    Container for prepared chat context supporting both dictionary
    and attribute access (e.g. prep['retrieved_chunks'] or prep.retrieved_chunks).
    """
    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"'PreparedContext' has no attribute '{name}'")

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value


def prepare_context(
    message: str,
    user: Optional[Any] = None,
    context: Optional[Union[ChatContextPayload, Dict[str, Any]]] = None,
    history: Optional[List[Any]] = None,
    conversation_id: Optional[str] = None,
) -> PreparedContext:
    """
    Refactored preparation phase of the chat pipeline:
    Validates message greetings, scope constraints, performs RAG retrieval,
    and builds prompt messages along with tool results and retrieved chunks.
    """
    conv_id = conversation_id or str(uuid.uuid4())
    user_msg = message.strip()

    # 1. Greeting Check
    has_bengali = any('\u0980' <= ch <= '\u09FF' for ch in user_msg)
    is_en = not has_bengali and any('a' <= ch.lower() <= 'z' for ch in user_msg)

    if _is_greeting(user_msg):
        early = (
            "Hello! I am your FieldForesight Agricultural Assistant. "
            "Feel free to ask any question regarding crop care, irrigation, fertilizer management, "
            "pest control, or yield forecasts."
            if is_en
            else (
                "আসসালামু আলাইকুম! আমি ফিল্ডফোরসাইট কৃষি সহকারী। "
                "আপনার ফসলের পরিচর্যা, সেচ, সার প্রয়োগ, রোগবালাই দমন বা ফলনের পূর্বাভাস সংক্রান্ত "
                "যেকোনো প্রশ্ন করতে পারেন।"
            )
        )
        return PreparedContext({
            "conversation_id": conv_id,
            "user": user,
            "context": context,
            "retrieved_chunks": [],
            "tool_results": [],
            "sources": [],
            "messages": [],
            "early_reply": early,
            "target_model": DEFAULT_MODEL,
            "prompt_tokens": 0,
            "user_message": user_msg,
        })

    # 2. Scope Check
    if not _is_agri_scope(user_msg):
        return PreparedContext({
            "conversation_id": conv_id,
            "user": user,
            "context": context,
            "retrieved_chunks": [],
            "tool_results": [],
            "sources": [],
            "messages": [],
            "early_reply": (
                "দুঃখিত, আমি শুধুমাত্র কৃষি, ফসল ব্যবস্থাপনা, সার ও রোগবালাই এবং "
                "FieldForesight প্ল্যাটফর্ম সম্পর্কিত তথ্যে সহায়তা করতে পারি। "
                "অন্যান্য বিষয়ে তথ্য দেওয়ার সুযোগ আমার নেই।"
            ),
            "target_model": DEFAULT_MODEL,
            "prompt_tokens": 0,
            "user_message": user_msg,
        })

    # 3. Context & RAG Retrieval
    crop = None
    region = None
    predicted_yield = None

    if context:
        if isinstance(context, dict):
            crop = context.get("crop")
            region = context.get("region")
            predicted_yield = context.get("predicted_yield")
        else:
            crop = getattr(context, "crop", None)
            region = getattr(context, "region", None)
            predicted_yield = getattr(context, "predicted_yield", None)

    retrieved_chunks = retrieve(query=user_msg, crop=crop, k=3)
    tool_results: List[Dict[str, Any]] = []

    sources: List[str] = []
    guideline_context_parts = []
    for c in retrieved_chunks:
        source_label = f"{c['title']} ({c['section']})"
        if source_label not in sources:
            sources.append(source_label)
        guideline_context_parts.append(
            f"--- সোর্স: {source_label} ---\n{c['text']}"
        )

    guidelines_text = "\n\n".join(guideline_context_parts) if guideline_context_parts else ""

    # Build prompt instructions
    system_instruction = (
        "You are 'FieldForesight Krishi Sahakari' (কৃষি সহকারী), an expert agricultural AI assistant in Bangladesh.\n"
        "STRICT SAFETY & FACTUAL RULES:\n"
        "1. GROUNDING: Answer strictly based on the provided Bangladesh agricultural guidelines (BRRI/BARI/DAE). "
        "If the document does not contain reliable information on the topic, clearly state: "
        "'এ বিষয়ে আমার কাছে সুনির্দিষ্ট নির্ভরযোগ্য তথ্য নেই। সঠিক তথ্যের জন্য স্থানীয় উপ-সহকারী কৃষি কর্মকর্তা (SAAO) বা কৃষি কল সেন্টারে (১৬১২৩) যোগাযোগ করুন।'\n"
        "2. PESTICIDES & DOSAGES: NEVER invent chemical dosages, spray proportions, or milliliter/gram numbers that are not explicitly stated in the document. "
        "Always advise the farmer to consult their local Sub-Assistant Agricultural Officer (SAAO / উপ-সহকারী কৃষি কর্মকর্তা) or call 16123 before spraying chemicals.\n"
        "3. LANGUAGE: Answer in the same language the user writes in (Bangla, English, or Banglish translated to clear Bangla).\n"
        "4. TONE: Respectful, clear, practical, and farmer-friendly."
    )

    context_details = []
    if crop:
        context_details.append(f"ফসল (Crop): {crop}")
    if region:
        context_details.append(f"অঞ্চল (Region): {region}")
    if predicted_yield is not None:
        context_details.append(f"পূর্বাভাসকৃত ফলন: {predicted_yield:.2f} t/ha")

    user_prompt_content = ""
    if context_details:
        user_prompt_content += "কৃষকের বর্তমান ড্যাশবোর্ড প্রসঙ্গ:\n" + "\n".join(context_details) + "\n\n"

    if guidelines_text:
        user_prompt_content += f"সরকারি কৃষি গবেষণা নির্দেশিকা (Verified Knowledge Base):\n{guidelines_text}\n\n"
    else:
        user_prompt_content += "সরকারি নির্দেশিকা: এই সুনির্দিষ্ট প্রশ্নের কোনো তথ্যভাণ্ডার চাঙ্ক মেলেনি।\n\n"

    user_prompt_content += f"কৃষকের প্রশ্ন: {user_msg}"

    api_messages: List[Dict[str, str]] = [
        {"role": "system", "content": system_instruction}
    ]

    if history:
        for hist_item in history[-6:]:
            if isinstance(hist_item, dict):
                r = hist_item.get("role", "user")
                c = hist_item.get("content", "")
            else:
                r = getattr(hist_item, "role", "user")
                c = getattr(hist_item, "content", "")
            role = "user" if r == "user" else "assistant"
            api_messages.append({"role": role, "content": c})

    api_messages.append({"role": "user", "content": user_prompt_content})

    target_model = route_model(user_msg, DEFAULT_MODEL)
    prompt_tokens = estimate_tokens(str(api_messages))

    return PreparedContext({
        "conversation_id": conv_id,
        "user": user,
        "context": context,
        "retrieved_chunks": retrieved_chunks,
        "tool_results": tool_results,
        "sources": sources,
        "messages": api_messages,
        "early_reply": None,
        "target_model": target_model,
        "prompt_tokens": prompt_tokens,
        "user_message": user_msg,
    })


def generate(
    messages: List[Dict[str, str]],
    retrieved_chunks: Optional[List[Dict[str, Any]]] = None,
    target_model: Optional[str] = None,
    sources: Optional[List[str]] = None,
) -> str:
    """
    Generation phase:
    Evaluates response cache, token optimizer modes (replay, dry_run, live),
    calls Groq completion with failover models, and falls back to grounded local response.
    """
    if retrieved_chunks is None:
        retrieved_chunks = []

    # Extract user message for token optimizer matching
    user_msg = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            content = msg.get("content", "")
            if "কৃষকের প্রশ্ন: " in content:
                user_msg = content.split("কৃষকের প্রশ্ন: ")[-1].strip()
            else:
                user_msg = content.strip()
            break

    model = target_model or route_model(user_msg or "query", DEFAULT_MODEL)
    prompt_tokens = estimate_tokens(str(messages))
    mode = get_current_mode()

    # A. Exact Cache Check
    cached = get_cached_response(model, messages)
    if cached:
        content = cached["content"]
        comp_tokens = estimate_tokens(content)
        log_token_usage("cache", model, prompt_tokens, comp_tokens, cached=True, is_live=False)
        return content

    # B. Replay Mode (Zero API calls, uses verified ground-truth responses)
    if mode == "replay":
        replay_obj = get_replay_response(prompt_text=user_msg)
        if replay_obj and "reply" in replay_obj:
            content = replay_obj["reply"]
            comp_tokens = estimate_tokens(content)
            store_cached_response(model, messages, content)
            log_token_usage("replay", model, prompt_tokens, comp_tokens, cached=False, is_live=False)
            return content

    # C. Dry Run Mode (Estimates tokens and logs without external calls)
    if mode == "dry_run":
        est_completion = 120
        log_token_usage("dry_run", model, prompt_tokens, est_completion, cached=False, is_live=False)
        if retrieved_chunks:
            return (
                f"[Dry-Run Estimate: ~{prompt_tokens + est_completion} tokens] কৃষি গবেষণা নির্দেশিকা অনুযায়ী:\n\n"
                f"{retrieved_chunks[0]['text'][:300]}...\n\n"
                f"⚠️ কীটনাশক বা সারের সঠিক প্রয়োগের পূর্বে আপনার এলাকার উপ-সহকারী কৃষি কর্মকর্তা (SAAO) "
                f"অথবা কৃষি কল সেন্টারে (১৬১২৩) যোগাযোগ করুন।"
            )
        else:
            return (
                f"[Dry-Run Estimate: ~{prompt_tokens + est_completion} tokens] "
                f"এ বিষয়ে আমার কাছে সুনির্দিষ্ট নির্ভরযোগ্য তথ্য পাওয়া যায়নি।"
            )

    # D. Live Mode: Prioritize Gemini 1.5 Flash (1M TPM free tier), then Groq
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    if gemini_key:
        try:
            gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent?key={gemini_key}"
            sys_prompt = next((m["content"] for m in messages if m["role"] == "system"), "")
            contents = []
            for m in messages:
                if m["role"] == "system":
                    continue
                role = "user" if m["role"] == "user" else "model"
                contents.append({"role": role, "parts": [{"text": m["content"]}]})
            payload = {
                "systemInstruction": {"parts": [{"text": sys_prompt}]},
                "contents": contents,
                "generationConfig": {"temperature": 0.25, "maxOutputTokens": 600},
            }
            start_t = time.time()
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                candidates = resp.json().get("candidates", [])
                if candidates:
                    reply_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                    if reply_text:
                        latency = (time.time() - start_t) * 1000.0
                        comp_tokens = estimate_tokens(reply_text)
                        store_cached_response(gemini_model, messages, reply_text)
                        log_token_usage("live", gemini_model, prompt_tokens, comp_tokens, cached=False, is_live=True, latency_ms=latency)
                        return reply_text
        except Exception:
            pass

    groq_api_key = _get_groq_api_key()
    if groq_api_key and mode == "live":
        register_live_call_intent(model)

        env_model = os.getenv("GROQ_MODEL", "").strip()
        candidate_models = [m for m in [env_model, model, FALLBACK_MODEL, "qwen/qwen3.8-27b", "llama-3.3-70b-versatile"] if m]
        seen = set()
        models_to_try = [m for m in candidate_models if not (m in seen or seen.add(m))]

        for cand_model in models_to_try:
            try:
                start_t = time.time()
                resp = requests.post(
                    GROQ_API_URL,
                    headers={
                        "Authorization": f"Bearer {groq_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": cand_model,
                        "messages": messages,
                        "temperature": 0.2,
                        "max_tokens": 500,
                    },
                    timeout=10,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    reply_text = data["choices"][0]["message"]["content"].strip()
                    latency = (time.time() - start_t) * 1000.0
                    comp_tokens = estimate_tokens(reply_text)

                    store_cached_response(cand_model, messages, reply_text)
                    log_token_usage("live", cand_model, prompt_tokens, comp_tokens, cached=False, is_live=True, latency_ms=latency)

                    return reply_text
            except Exception:
                continue

    # 5. Local Fallback (when Groq is unreachable or offline)
    if retrieved_chunks:
        return (
            f"কৃষি গবেষণা নির্দেশিকা অনুযায়ী:\n\n"
            f"{retrieved_chunks[0]['text'][:300]}...\n\n"
            f"⚠️ কীটনাশক বা সারের সঠিক প্রয়োগের পূর্বে আপনার এলাকার উপ-সহকারী কৃষি কর্মকর্তা (SAAO) "
            f"অথবা কৃষি কল সেন্টারে (১৬১২৩) যোগাযোগ করার পরামর্শ দেওয়া হলো।"
        )
    else:
        return (
            "এ বিষয়ে আমার কাছে সুনির্দিষ্ট নির্ভরযোগ্য তথ্য পাওয়া যায়নি। "
            "আপনার ফসলের সঠিক রোগবালাই বা সার ব্যবস্থাপনার জন্য স্থানীয় উপ-সহকারী কৃষি কর্মকর্তা (SAAO) "
            "অথবা কৃষি কল সেন্টারে (১৬১২৩) যোগাযোগ করুন।"
        )


def generate_chat_response(req: ChatRequest, user: Optional[Any] = None) -> ChatResponse:
    """
    Main entry point for full-reply chat: orchestrates prepare_context and generate.
    """
    prep = prepare_context(
        message=req.message,
        user=user,
        context=req.context,
        history=req.history,
        conversation_id=req.conversation_id,
    )

    if prep.get("early_reply"):
        return ChatResponse(
            reply=prep["early_reply"],
            conversation_id=prep["conversation_id"],
            sources=prep["sources"],
        )

    reply_text = generate(
        messages=prep["messages"],
        retrieved_chunks=prep["retrieved_chunks"],
        target_model=prep["target_model"],
        sources=prep["sources"],
    )

    return ChatResponse(
        reply=reply_text,
        conversation_id=prep["conversation_id"],
        sources=prep["sources"],
    )
