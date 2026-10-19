import os
import json
import requests
from typing import Dict, Any, List

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def _get_env_fallback(key: str, default: str = "") -> str:
    val = os.getenv(key)
    if val:
        return val
    # Search common .env locations
    candidates = [
        os.path.join(os.path.dirname(__file__), "..", "..", ".env"),
        os.path.join(os.getcwd(), ".env"),
        ".env",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            if k.strip() == key:
                                return v.strip().strip("'\"")
            except Exception:
                pass
    return default

GROQ_API_KEY = _get_env_fallback("GROQ_API_KEY", "")
DEFAULT_GROQ_MODEL = _get_env_fallback("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"


SYSTEM_PROMPT = """তুমি বাংলাদেশ কৃষি গবেষণা কাউন্সিল (BARC), বাংলাদেশ ধান গবেষণা ইনস্টিটিউট (BRRI) ও কৃষি সম্প্রসারণ অধিদপ্তর (DAE)-এর একজন প্রধান কৃষি বিজ্ঞানী ও অভিজ্ঞ মাঠ পরামর্শক।

তোমার দায়িত্ব:
প্রদত্ত ফসলের নাম, জাত (Variety), অঞ্চল (District), পূর্বাভাসকৃত সম্ভাব্য ফলন এবং ঝুঁকি স্তরের (Risk Level) উপর ভিত্তি করে সাধারণ কৃষক ভাইদের জন্য অত্যন্ত সহজ, সাবলীল, বোধগম্য ও বাস্তবমুখী বাংলা ভাষায় পরামর্শ প্রদান করা।

নির্দেশনা ও শৈলী (Guidelines):
১. ভাষা হবে প্রমিত এবং কৃষকবান্ধব বাংলা। কোনো অপ্রয়োজনীয় ইংরেজি বা জটিল টেকনিক্যাল পরিভাষা ব্যবহার করবে না।
২. পরামর্শে স্পষ্ট ও সুনির্দিষ্ট হিসাব থাকবে (যেমন: শতকে বা বিঘায় ইউরিয়া, ডিএপি বা পটাশ সারের মাত্রা, অথবা সেচের সময়সূচি)।
৩. যদি উচ্চ বা মাঝারি ঝুঁকি থাকে, তবে অবিলম্বে করণীয় প্রতিরোধমূলক পদক্ষেপ স্পষ্টভাবে উল্লেখ করবে।
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
) -> Dict[str, Any]:
    """
    Calls Groq API (Llama-3.3-70b-versatile) to generate contextual agricultural Bangla advisory.
    Falls back gracefully to expert agronomic rules if key is missing or request fails.
    """
    api_key = os.getenv("GROQ_API_KEY") or GROQ_API_KEY
    risk_desc = ", ".join(risk_factors) if risk_factors else "স্বাভাবিক অবস্থা"
    ndvi_info = ndvi_status if ndvi_status else "সন্তোষজনক উপগ্রহ চিত্র"

    user_prompt = (
        f"ফসল: {crop}\n"
        f"অনুমোদিত জাত: {variety}\n"
        f"অঞ্চল / জেলা: {region}\n"
        f"পূর্বাভাসকৃত ফলন: {predicted_yield:.2f} টন/হেক্টর\n"
        f"শনাক্তকৃত ঝুঁকি স্তর: {risk_level.upper()}\n"
        f"ঝুঁকির কারণসমূহ: {risk_desc}\n"
        f"স্যাটেলাইট ক্যানোপি অবস্থা (NDVI): {ndvi_info}\n"
        f"চাষের ধরন: {cropping_type}\n\n"
        f"উপরোক্ত তথ্যের ভিত্তিতে কৃষকের জন্য খাঁটি বাংলায় বাস্তবসম্মত পরামর্শ ও ৩টি সুস্পষ্ট অ্যাকশন আইটেম সহ JSON তৈরি করো।"
    )

    if api_key:
        candidate_models = [
            DEFAULT_GROQ_MODEL,
            "openai/gpt-oss-120b",
            "qwen/qwen3.8-27b",
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
        ]
        # Deduplicate preserving order
        seen = set()
        models_to_try = [m for m in candidate_models if m and not (m in seen or seen.add(m))]

        for model_candidate in models_to_try:
            try:
                headers = {
                    "Authorization": f"Bearer {api_key.strip()}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": model_candidate,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
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
                    return {
                        "advisory_text": parsed.get("advisory_text", ""),
                        "action_items": parsed.get("action_items", []),
                        "precaution_alert": parsed.get("precaution_alert", ""),
                        "llm_provider": "groq",
                        "llm_model": model_candidate,
                    }
                elif response.status_code == 404:
                    # Model not available on this tier/key, try next candidate
                    continue
                else:
                    print(f"Groq API Error {response.status_code} ({model_candidate}): {response.text}")
            except Exception as e:
                print(f"Groq API call exception ({model_candidate}): {e}")

    # Fallback to intelligent agronomic rule engine in authentic Bangla
    return generate_fallback_advisory(
        crop=crop,
        region=region,
        variety=variety,
        predicted_yield=predicted_yield,
        risk_level=risk_level,
        risk_factors=risk_factors,
    )


def generate_fallback_advisory(
    crop: str,
    region: str,
    variety: str,
    predicted_yield: float,
    risk_level: str,
    risk_factors: List[str] | None = None,
) -> Dict[str, Any]:
    """
    Expert rule-based fallback advisory modeled after Bangladesh DAE / BRRI / BARI recommendations.
    Provides immediate response when Groq API key is not configured or offline.
    """
    variety_clean = variety.replace("_", " ")

    if risk_level == "high":
        advisory_text = (
            f"{region} অঞ্চলে {variety_clean} জাতের {crop} আবাদে সম্ভাব্য ফলন বিপর্যয় এড়াতে অবিলম্বে মাঠ পরিদর্শন করুন। "
            f"পূর্বাভাসকৃত ফলন ({predicted_yield:.2f} টন/হেক্টর) স্বাভাবিকের চেয়ে কম হওয়ায় অতিরিক্ত যত্ন ও পরিমিত সার প্রয়োগ নিশ্চিত করা জরুরি।"
        )
        action_items = [
            f"জমিতে ইউরিয়া ও পটাশ সারের শেষ কিস্তি সুষম মাত্রায় প্রয়োগ করুন এবং ৩-৪ সেমি দাঁড়ানো পানি নিশ্চিত করুন।",
            f"শীথ ব্লাইট বা পাতামোড়ানো পোকা দমনে অনুমোদিত বালাইনাশক স্প্রে করুন এবং আক্রান্ত গাছ আলাদা করুন।",
            f"স্থানীয় উপজেলা কৃষি কর্মকর্তা অথবা উপ-সহকারী কৃষি কর্মকর্তার সাথে তাৎক্ষণিক পরামর্শ নিন।",
        ]
        precaution = f"সতর্কতা: জমিতে তীব্র আর্দ্রতা ঘাটতি বা ব্লাস্ট রোগের লক্ষণ দেখা দিলে অবিলম্বে স্প্রে করুন।"
    elif risk_level == "medium":
        advisory_text = (
            f"{region} অঞ্চলের বর্তমান আবহাওয়া ও মাটির অবস্থা বিবেচনায় {variety_clean} জাতের {crop} থেকে কাঙ্ক্ষিত ফলন "
            f"({predicted_yield:.2f} টন/হেক্টর) অর্জনে সুষম সেচ ও আগাছা দমন নিশ্চিত করুন।"
        )
        action_items = [
            f"গাছের বৃদ্ধি নিশ্চিত করতে শেষ দফায় শতক প্রতি ৩০০ গ্রাম ইউরিয়া ও ২০০ গ্রাম এমওপি সার প্রয়োগ করুন।",
            f"মাটির ভেজা অবস্থা বজায় রাখতে সান্ধ্যকালীন হালকা সেচ প্রদান করুন।",
            f"নিয়মিত আলোর ফাঁদ ব্যবহার করে ক্ষতিকর পোকার উপস্থিতি যাচাই করুন।",
        ]
        precaution = f"পরামর্শ: আগামী ৭২ ঘণ্টার মধ্যে হালকা সেচ দিলে ফলনের গুণগত মান বৃদ্ধি পাবে।"
    else:
        advisory_text = (
            f"{region} অঞ্চলে {variety_clean} জাতের {crop} চাষের বর্তমান অবস্থা অত্যন্ত আশাব্যঞ্জক। "
            f"পূর্বাভাস অনুযায়ী ফলন প্রায় {predicted_yield:.2f} টন/হেক্টর অর্জিত হওয়ার সম্ভাবনা রয়েছে।"
        )
        action_items = [
            f"ফসল পরিপক্ক হওয়া পর্যন্ত নিয়মিত পানির স্তর পর্যবেক্ষণ করুন ও অতিরিক্ত পানি নিষ্কাশনের ব্যবস্থা রাখুন।",
            f"দানার পূর্ণ পুষ্টির জন্য বিঘাপ্রতি প্রয়োজনীয় দানাদার মাইক্রো-নিউট্রিয়েন্ট প্রয়োগ বজায় রাখুন।",
            f"ফসল কাটার উপযুক্ত সময় নির্ধারণে ৮০% দানা সোনালী বর্ণ ধারণ করা পর্যন্ত পর্যবেক্ষণ করুন।",
        ]
        precaution = f"অনুকূল অবস্থা: আবহাওয়া ফসল বৃদ্ধির জন্য অনুকূল রয়েছে।"

    return {
        "advisory_text": advisory_text,
        "action_items": action_items,
        "precaution_alert": precaution,
        "llm_provider": "rule_engine",
        "llm_model": "BARI-BRRI-Agronomic-Expert-v1",
    }
