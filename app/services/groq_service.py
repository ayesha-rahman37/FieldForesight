import os
import json
import time
from pathlib import Path
import requests
from typing import Dict, Any, List, Optional, Iterator
from dotenv import load_dotenv

from app.services.token_optimizer import (
    get_current_mode,
    get_cached_response,
    store_cached_response,
    register_live_call_intent,
    get_replay_response,
    estimate_tokens,
    log_token_usage,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = REPO_ROOT / ".env"
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"


def _get_env_fallback(key: str, default: str = "") -> str:
    load_dotenv(ENV_PATH, override=True)
    val = os.getenv(key)
    if val:
        return val.strip().strip("'\"")
    if ENV_PATH.exists():
        try:
            with open(ENV_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        if k.strip() == key:
                            return v.strip().strip("'\"")
        except Exception:
            pass
    return default


SYSTEM_PROMPT = """তুমি বাংলাদেশ কৃষি গবেষণা কাউন্সিল (BARC), বাংলাদেশ ধান গবেষণা ইনস্টিটিউট (BRRI) ও কৃষি সম্প্রসারণ অধিদপ্তর (DAE)-এর একজন প্রধান কৃষি বিজ্ঞানী ও অভিজ্ঞ মাঠ পরামর্শক।

তোমার দায়িত্ব:
প্রদত্ত ফসলের নাম, জাত (Variety), অঞ্চল (District), পূর্বাভাসকৃত সম্ভাব্য ফলন, বৃষ্টিপাত ও তাপমাত্রার পরিবর্তন এবং ঝুঁকি স্তরের (Risk Level) উপর ভিত্তি করে সাধারণ কৃষক ভাইদের জন্য অত্যন্ত সহজ, সাবলীল, বোধগম্য ও বাস্তবমুখী বাংলা ভাষায় পরামর্শ প্রদান করা।

নির্দেশনা ও শৈলী (Guidelines):
১. ভাষা হবে প্রমিত এবং কৃষকবান্ধব বাংলা। কোনো অপ্রয়োজনীয় ইংরেজি বা জটিল টেকনিক্যাল পরিভাষা ব্যবহার করবে না।
২. পরামর্শে স্পষ্ট ও সুনির্দিষ্ট হিসাব থাকবে (যেমন: শতকে বা বিঘায় ইউরিয়া, ডিএপি বা পটাশ সারের মাত্রা, অথবা সেচের সময়সূচি)।
৩. যদি বৃষ্টিপাত বা তাপমাত্রা পরিবর্তনের সিমুলেশন থাকে (যেমন: খরা, অতিবৃষ্টি বা তাপপ্রবাহ), তবে সেই পরিস্থিতির সাথে সামঞ্জস্যপূর্ণ সুনির্দিষ্ট পদক্ষেপ উল্লেখ করবে।
৪. উত্তরটি সর্বদা বৈধ JSON ফরম্যাটে প্রদান করবে, অন্য কোনো ভূমিকা বা সমাপ্তি বাক্য লিখবে না।

JSON ফরম্যাট:
{
  "advisory_text": "কৃষকের জন্য ২-৩ বাক্যে মূল সারসংক্ষেপ ও প্রধান পরামর্শ।",
  "action_items": [
    "পদক্ষেপ ১: সার বা মাটির পরিচর্যা বিষয়ক সুনির্দিষ্ট করণীয়",
    "পদক্ষেপ ২: সেচ বা পানি নিষ্কাশন বিষয়ক সুনির্দিষ্ট নির্দেশনা",
    "পদক্ষেপ ৩: বালাই দমন বা রোগ প্রতিরোধমূলক নির্দেশনা"
  ],
  "precaution_alert": "জরুরি সতর্কতা সংকেত (১ বাক্য)"
}
"""


def generate_bangla_advisory_groq(
    crop: str,
    region: str,
    variety: str,
    predicted_yield: float,
    risk_level: str,
    risk_factors: List[str] | None = None,
    ndvi_status: str | None = None,
    cropping_type: str = "single",
    rainfall_adjustment_percent: float = 0.0,
    temperature_adjustment_percent: float = 0.0,
) -> Dict[str, Any]:
    """
    Calls Groq API (Llama-3.3-70b-versatile) to generate contextual agricultural Bangla advisory.
    Falls back gracefully to expert agronomic rules if key is missing or request fails.
    """
    api_key = _get_env_fallback("GROQ_API_KEY", "")
    default_model = _get_env_fallback("GROQ_MODEL", "llama-3.3-70b-versatile")
    risk_desc = ", ".join(risk_factors) if risk_factors else "স্বাভাবিক অবস্থা"
    ndvi_info = ndvi_status if ndvi_status else "সন্তোষজনক উপগ্রহ চিত্র"
    temp_shift_c = temperature_adjustment_percent / 10.0

    climate_sim_line = ""
    if abs(rainfall_adjustment_percent) > 0.1 or abs(temp_shift_c) > 0.05:
        climate_sim_line = (
            f"সিমুলেশন জলবায়ু পরিবর্তন: বৃষ্টিপাত {rainfall_adjustment_percent:+.0f}%, "
            f"তাপমাত্রা {temp_shift_c:+.1f}°C\n"
        )

    user_prompt = (
        f"ফসল: {crop}\n"
        f"অনুমোদিত জাত: {variety}\n"
        f"অঞ্চল / জেলা: {region}\n"
        f"পূর্বাভাসকৃত ফলন: {predicted_yield:.2f} টন/হেক্টর\n"
        f"{climate_sim_line}"
        f"শনাক্তকৃত ঝুঁকি স্তর: {risk_level.upper()}\n"
        f"ঝুঁকির কারণসমূহ: {risk_desc}\n"
        f"স্যাটেলাইট ক্যানোপি অবস্থা (NDVI): {ndvi_info}\n"
        f"চাষের ধরন: {cropping_type}\n\n"
        f"উপরোক্ত তথ্যের ভিত্তিতে কৃষকের জন্য খাঁটি বাংলায় বাস্তবসম্মত পরামর্শ ও ৩টি সুস্পষ্ট অ্যাকশন আইটেম সহ JSON তৈরি করো।"
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    mode = get_current_mode()
    prompt_tokens = estimate_tokens(SYSTEM_PROMPT + user_prompt)

    # 1. Exact Cache Check (Applies to all modes to save calls)
    cached = get_cached_response(default_model, messages)
    if cached:
        try:
            parsed = json.loads(cached["content"])
            comp_tokens = estimate_tokens(cached["content"])
            log_token_usage("cache", default_model, prompt_tokens, comp_tokens, cached=True, is_live=False)
            return {
                "advisory_text": parsed.get("advisory_text", ""),
                "action_items": parsed.get("action_items", []),
                "precaution_alert": parsed.get("precaution_alert", ""),
                "llm_provider": "cache",
                "llm_model": default_model,
            }
        except Exception:
            pass

    # 2. Replay Mode (Zero API calls, deterministic grounded responses)
    if mode == "replay":
        replay_data = get_replay_response(prompt_text=user_prompt)
        if replay_data and "advisory_text" in replay_data:
            content_str = json.dumps(replay_data, ensure_ascii=False)
            store_cached_response(default_model, messages, content_str)
            comp_tokens = estimate_tokens(content_str)
            log_token_usage("replay", default_model, prompt_tokens, comp_tokens, cached=False, is_live=False)
            return {
                "advisory_text": replay_data.get("advisory_text", ""),
                "action_items": replay_data.get("action_items", []),
                "precaution_alert": replay_data.get("precaution_alert", ""),
                "llm_provider": "replay",
                "llm_model": default_model,
            }

    # 3. Dry Run Mode (Calculates length & token estimates without making network calls)
    if mode == "dry_run":
        est_completion_tokens = 150
        log_token_usage("dry_run", default_model, prompt_tokens, est_completion_tokens, cached=False, is_live=False)
        fallback = generate_fallback_advisory(
            crop=crop,
            region=region,
            variety=variety,
            predicted_yield=predicted_yield,
            risk_level=risk_level,
            risk_factors=risk_factors,
            rainfall_adjustment_percent=rainfall_adjustment_percent,
            temperature_adjustment_percent=temperature_adjustment_percent,
        )
        fallback["llm_provider"] = "dry_run"
        fallback["llm_model"] = default_model
        return fallback

    # 4. Live Mode: Prioritize Gemini 1.5 Flash (1M TPM free tier) when configured, fallback to Groq
    gemini_key = _get_env_fallback("GEMINI_API_KEY")
    if gemini_key and mode == "live":
        try:
            gemini_model = _get_env_fallback("GEMINI_MODEL", "gemini-1.5-flash").strip()
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent?key={gemini_key}"
            payload = {
                "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
                "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
                "generationConfig": {
                    "temperature": 0.25,
                    "maxOutputTokens": 600,
                    "responseMimeType": "application/json",
                },
            }
            start_t = time.time()
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                candidates = resp.json().get("candidates", [])
                if candidates:
                    raw_json = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                    parsed = json.loads(raw_json)
                    latency = (time.time() - start_t) * 1000.0
                    comp_tokens = estimate_tokens(raw_json)
                    store_cached_response(gemini_model, messages, raw_json)
                    log_token_usage("live", gemini_model, prompt_tokens, comp_tokens, cached=False, is_live=True, latency_ms=latency)
                    return {
                        "advisory_text": parsed.get("advisory_text", ""),
                        "action_items": parsed.get("action_items", []),
                        "precaution_alert": parsed.get("precaution_alert", ""),
                        "llm_provider": "gemini",
                        "llm_model": gemini_model,
                    }
        except Exception:
            pass

    # Fallback to Groq if Gemini key is absent or encounters error
    if api_key and mode == "live":
        register_live_call_intent(default_model)

        candidate_models = [
            default_model,
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
        ]
        seen = set()
        models_to_try = [m for m in candidate_models if m and not (m in seen or seen.add(m))]

        for model_candidate in models_to_try:
            try:
                start_t = time.time()
                headers = {
                    "Authorization": f"Bearer {api_key.strip()}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": model_candidate,
                    "messages": messages,
                    "temperature": 0.35,
                    "max_tokens": 600,
                    "response_format": {"type": "json_object"},
                }

                response = requests.post(
                    GROQ_ENDPOINT,
                    headers=headers,
                    json=payload,
                    timeout=8.5,
                )

                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"].strip()
                    parsed = json.loads(content)
                    latency = (time.time() - start_t) * 1000.0
                    comp_tokens = estimate_tokens(content)

                    # Store in exact cache
                    store_cached_response(model_candidate, messages, content)
                    log_token_usage("live", model_candidate, prompt_tokens, comp_tokens, cached=False, is_live=True, latency_ms=latency)

                    return {
                        "advisory_text": parsed.get("advisory_text", ""),
                        "action_items": parsed.get("action_items", []),
                        "precaution_alert": parsed.get("precaution_alert", ""),
                        "llm_provider": "groq",
                        "llm_model": model_candidate,
                    }
                elif response.status_code == 404:
                    continue
                else:
                    import sys
                    print(f"Groq API Error {response.status_code} ({model_candidate}): {response.text}", file=sys.stderr)
            except Exception as e:
                import sys
                print(f"Groq API call exception ({model_candidate}): {e}", file=sys.stderr)

    return generate_fallback_advisory(
        crop=crop,
        region=region,
        variety=variety,
        predicted_yield=predicted_yield,
        risk_level=risk_level,
        risk_factors=risk_factors,
        rainfall_adjustment_percent=rainfall_adjustment_percent,
        temperature_adjustment_percent=temperature_adjustment_percent,
    )


def generate_fallback_advisory(
    crop: str,
    region: str,
    variety: str,
    predicted_yield: float,
    risk_level: str,
    risk_factors: List[str] | None = None,
    rainfall_adjustment_percent: float = 0.0,
    temperature_adjustment_percent: float = 0.0,
) -> Dict[str, Any]:
    """
    Expert rule-based fallback advisory modeled after Bangladesh DAE / BRRI / BARI recommendations.
    Dynamically adapts to simulated rainfall and temperature changes when Groq API key is offline.
    """
    variety_clean = variety.replace("_", " ")
    temp_shift_c = temperature_adjustment_percent / 10.0

    # Check if user simulated significant rainfall or temperature shifts
    climate_clause = ""
    if rainfall_adjustment_percent <= -20:
        climate_clause = f" বৃষ্টিপাত {abs(rainfall_adjustment_percent):.0f}% কমে যাওয়ায় মাটির আর্দ্রতা সংরক্ষণে বিশেষ সেচ ব্যবস্থাপনা জরুরি।"
    elif rainfall_adjustment_percent >= 20:
        climate_clause = f" অতিরিক্ত বৃষ্টিপাত ({rainfall_adjustment_percent:+.0f}%) বিবেচনায় জমিতে জলাবদ্ধতা রোধে দ্রুত পানি নিষ্কাশন নালা পরিষ্কার রাখুন।"
    if temp_shift_c >= 1.5:
        climate_clause += f" তাপমাত্রা {temp_shift_c:+.1f}°সে বৃদ্ধি পাওয়ায় হিট শক এড়াতে জমিতে ২-৩ ইঞ্চি পানি ধরে রাখুন।"
    elif temp_shift_c <= -1.5:
        climate_clause += f" তাপমাত্রা {abs(temp_shift_c):.1f}°সে হ্রাস পাওয়ায় ছত্রাকজনিত ব্লাইট রোগ প্রতিরোধে সতর্ক থাকুন।"

    if risk_level == "high":
        advisory_text = (
            f"{region} অঞ্চলে {variety_clean} জাতের {crop} আবাদে সম্ভাব্য ফলন বিপর্যয় এড়াতে অবিলম্বে মাঠ পরিদর্শন করুন। "
            f"পূর্বাভাসকৃত ফলন ({predicted_yield:.2f} টন/হেক্টর) স্বাভাবিকের চেয়ে কম হওয়ায় অতিরিক্ত যত্ন ও পরিমিত সার প্রয়োগ নিশ্চিত করা জরুরি।"
            f"{climate_clause}"
        )
        action_items = [
            "জমিতে ইউরিয়া ও পটাশ সারের শেষ কিস্তি সুষম মাত্রায় প্রয়োগ করুন এবং ৩-৪ সেমি দাঁড়ানো পানি নিশ্চিত করুন।",
            "শীথ ব্লাইট বা পাতামোড়ানো পোকা দমনে অনুমোদিত বালাইনাশক স্প্রে করুন এবং আক্রান্ত গাছ আলাদা করুন।",
            "স্থানীয় উপজেলা কৃষি কর্মকর্তা অথবা উপ-সহকারী কৃষি কর্মকর্তার সাথে তাৎক্ষণিক পরামর্শ নিন।",
        ]
        precaution = "সতর্কতা: জমিতে তীব্র আর্দ্রতা ঘাটতি বা ব্লাস্ট রোগের লক্ষণ দেখা দিলে অবিলম্বে স্প্রে করুন।"
    elif risk_level == "medium":
        advisory_text = (
            f"{region} অঞ্চলের বর্তমান আবহাওয়া ও মাটির অবস্থা বিবেচনায় {variety_clean} জাতের {crop} থেকে কাঙ্ক্ষিত ফলন "
            f"({predicted_yield:.2f} টন/হেক্টর) অর্জনে সুষম সেচ ও আগাছা দমন নিশ্চিত করুন।"
            f"{climate_clause}"
        )
        action_items = [
            "গাছের বৃদ্ধি নিশ্চিত করতে শেষ পর্যায়ে শতক প্রতি ৩০০ গ্রাম ইউরিয়া ও ২০০ গ্রাম এমওপি সার প্রয়োগ করুন।",
            "মাটির ভেজা অবস্থা বজায় রাখতে সান্ধ্যকালীন হালকা সেচ প্রদান করুন।",
            "নিয়মিত আলোর ফাঁদ ব্যবহার করে ক্ষতিকর পোকার উপস্থিতি যাচাই করুন।",
        ]
        precaution = "পরামর্শ: আগামী ৭২ ঘণ্টার মধ্যে হালকা সেচ দিলে ফলনের গুণগত মান বৃদ্ধি পাবে।"
    else:
        advisory_text = (
            f"{region} অঞ্চলে {variety_clean} জাতের {crop} চাষের বর্তমান অবস্থা অত্যন্ত আশাব্যঞ্জক। "
            f"পূর্বাভাস অনুযায়ী ফলন প্রায় {predicted_yield:.2f} টন/হেক্টর অর্জিত হওয়ার সম্ভাবনা রয়েছে।"
            f"{climate_clause}"
        )
        action_items = [
            "ফসল পরিপক্ক হওয়া পর্যন্ত নিয়মিত পানির স্তর পর্যবেক্ষণ করুন ও অতিরিক্ত পানি নিষ্কাশনের ব্যবস্থা রাখুন।",
            "দানার পূর্ণ পুষ্টির জন্য বিঘাপ্রতি প্রয়োজনীয় দানাদার মাইক্রো-নিউট্রিয়েন্ট প্রয়োগ বজায় রাখুন।",
            "ফসল কাটার উপযুক্ত সময় নির্ধারণে ৮০% দানা সোনালী বর্ণ ধারণ করা পর্যন্ত পর্যবেক্ষণ করুন।",
        ]
        precaution = "অনুকূল অবস্থা: আবহাওয়া ফসল বৃদ্ধির জন্য অনুকূল রয়েছে।"

    if rainfall_adjustment_percent <= -20:
        action_items[1] = f"খরা পরিস্থিতি ({rainfall_adjustment_percent:+.0f}% বৃষ্টিপাত) মোকাবিলায় সপ্তাহে অন্তত ২ বার গভীর নলকূপের সেচ দিন ও মালচিং ব্যবহার করুন।"
        precaution = f"পরামর্শ: বৃষ্টিপাত {abs(rainfall_adjustment_percent):.0f}% কম থাকায় ফুল আসার সময় পানির ঘাটতি হতে দেবেন না।"
    elif rainfall_adjustment_percent >= 20:
        action_items[1] = f"অতিবৃষ্টি ({rainfall_adjustment_percent:+.0f}%) জনিত জলাবদ্ধতা এড়াতে আইলের নিষ্কাশন নালা খুলে দিন এবং উপরি সার প্রয়োগ সাময়িক স্থগিত রাখুন।"
        precaution = "পরামর্শ: অতিরিক্ত বৃষ্টিপাতের কারণে শিকড় পচা রোগ এড়াতে জমি থেকে দ্রুত অতিরিক্ত পানি বের করে দিন।"
    elif temp_shift_c >= 1.5:
        action_items[0] = f"তাপমাত্রা বৃদ্ধি ({temp_shift_c:+.1f}°সে) জনিত হিট স্ট্রেস কমাতে প্রতি লিটার পানিতে ১০ গ্রাম পটাশিয়াম নাইট্রেট মিশিয়ে বিকেলে স্প্রে করুন।"
        precaution = "পরামর্শ: উচ্চ তাপমাত্রায় পরাগায়ন ব্যাহত হতে পারে, তাই জমিতে পর্যাপ্ত রস বজায় রাখুন।"

    return {
        "advisory_text": advisory_text,
        "action_items": action_items,
        "precaution_alert": precaution,
        "llm_provider": "rule_engine",
        "llm_model": "BARI-BRRI-Agronomic-Expert-v1",
    }


def stream_completion(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
) -> Iterator[str]:
    """
    Streams text deltas from Groq API (OpenAI compatible SSE format).
    Yields chunks of text deltas. Reads token usage from final chunk/metadata
    if available; otherwise estimates token counts and logs with is_estimated=True.
    """
    selected_model = (
        model
        or _get_env_fallback("GROQ_MODEL", "qwen/qwen3.8-27b")
        or "qwen/qwen3.8-27b"
    )
    prompt_tokens = estimate_tokens(str(messages))
    mode = get_current_mode()

    # 1. Exact Cache Check
    cached = get_cached_response(selected_model, messages)
    if cached and cached.get("content"):
        content = cached["content"]
        comp_tokens = estimate_tokens(content)
        log_token_usage("cache", selected_model, prompt_tokens, comp_tokens, cached=True, is_live=False)
        words = content.split(" ")
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")
        return

    # 2. Replay Mode
    if mode == "replay":
        user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                content = m.get("content", "")
                if "কৃষকের প্রশ্ন: " in content:
                    user_msg = content.split("কৃষকের প্রশ্ন: ")[-1].strip()
                else:
                    user_msg = content.strip()
                break
        replay_obj = get_replay_response(prompt_text=user_msg)
        replay_text = (
            replay_obj.get("reply", "")
            if replay_obj
            else "এ বিষয়ে আমার কাছে সুনির্দিষ্ট নির্ভরযোগ্য তথ্য পাওয়া যায়নি।"
        )
        comp_tokens = estimate_tokens(replay_text)
        store_cached_response(selected_model, messages, replay_text)
        log_token_usage("replay", selected_model, prompt_tokens, comp_tokens, cached=False, is_live=False)
        words = replay_text.split(" ")
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")
        return

    # 3. Dry Run Mode
    if mode == "dry_run":
        est_completion = 120
        log_token_usage("dry_run", selected_model, prompt_tokens, est_completion, cached=False, is_live=False)
        dry_text = f"[Dry-Run Estimate: ~{prompt_tokens + est_completion} tokens] কৃষি গবেষণা নির্দেশিকা অনুযায়ী পরামর্শ প্রস্তুত।"
        words = dry_text.split(" ")
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")
        return

    # 4. Live Streaming Call
    api_key = _get_env_fallback("GROQ_API_KEY", "")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured")

    register_live_call_intent(selected_model)

    candidate_models = [
        selected_model,
        "qwen/qwen3.8-27b",
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
    ]
    seen = set()
    models_to_try = [m for m in candidate_models if m and not (m in seen or seen.add(m))]

    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json",
    }

    last_error: Optional[Exception] = None

    for cand_model in models_to_try:
        start_t = time.time()
        payload = {
            "model": cand_model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 500,
            "stream": True,
            "stream_options": {"include_usage": True},
        }

        try:
            resp = requests.post(
                GROQ_ENDPOINT,
                headers=headers,
                json=payload,
                stream=True,
                timeout=15,
            )

            if resp.status_code == 404:
                continue

            if resp.status_code != 200:
                raise RuntimeError(f"Groq API streaming error {resp.status_code}: {resp.text}")

            accumulated_text = []
            has_usage = False
            reported_prompt_tokens = prompt_tokens
            reported_comp_tokens = 0

            for line in resp.iter_lines():
                if not line:
                    continue
                decoded = line.decode("utf-8") if isinstance(line, bytes) else line
                if not decoded.startswith("data: "):
                    continue
                data_str = decoded[6:].strip()
                if data_str == "[DONE]":
                    break

                try:
                    chunk = json.loads(data_str)
                except Exception:
                    continue

                usage = chunk.get("usage")
                if usage and isinstance(usage, dict):
                    reported_prompt_tokens = usage.get("prompt_tokens", prompt_tokens)
                    reported_comp_tokens = usage.get("completion_tokens", 0)
                    has_usage = True

                choices = chunk.get("choices", [])
                if choices:
                    delta = choices[0].get("delta", {})
                    content_chunk = delta.get("content", "")
                    if content_chunk:
                        accumulated_text.append(content_chunk)
                        yield content_chunk

            full_text = "".join(accumulated_text).strip()
            latency = (time.time() - start_t) * 1000.0

            if not has_usage:
                reported_comp_tokens = estimate_tokens(full_text)
                log_token_usage(
                    "live",
                    cand_model,
                    reported_prompt_tokens,
                    reported_comp_tokens,
                    cached=False,
                    is_live=True,
                    latency_ms=latency,
                    is_estimated=True,
                )
            else:
                log_token_usage(
                    "live",
                    cand_model,
                    reported_prompt_tokens,
                    reported_comp_tokens,
                    cached=False,
                    is_live=True,
                    latency_ms=latency,
                    is_estimated=False,
                )

            if full_text:
                store_cached_response(cand_model, messages, full_text)

            return
        except Exception as exc:
            last_error = exc
            continue

    if last_error:
        raise last_error
    raise RuntimeError("All Groq streaming models failed to respond")

