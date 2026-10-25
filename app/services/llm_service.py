import os
from pathlib import Path
import requests
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = REPO_ROOT / ".env"
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"


def _get_env_key(key: str, default: str = "") -> str:
    load_dotenv(ENV_PATH, override=True)
    val = os.getenv(key)
    if val:
        return val.strip().strip("'\"")
    return default


def generate_llm_text(prompt: str, fallback_text: str) -> str:
    """
    Calls Groq API (Llama-3.3-70b-versatile) using GROQ_API_KEY from .env
    (or Google Gemini if GEMINI_API_KEY is configured).
    Falls back gracefully to fallback_text if keys are missing or request fails.
    """
    groq_key = _get_env_key("GROQ_API_KEY")
    groq_model = _get_env_key("GROQ_MODEL", "qwen/qwen3.8-27b")

    if groq_key:
        for model_name in [groq_model, "qwen/qwen3.8-27b", "openai/gpt-oss-20b", "llama-3.3-70b-versatile"]:
            try:
                headers = {
                    "Authorization": f"Bearer {groq_key}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": model_name,
                    "messages": [
                        {
                            "role": "system",
                            "content": "তুমি বাংলাদেশ কৃষি গবেষণা কাউন্সিল (BARC)-এর একজন কৃষি বিশেষজ্ঞ। সংক্ষেপে ২-৩ বাক্যে সহজ বাংলায় উত্তর দাও।",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.35,
                    "max_tokens": 280,
                }
                response = requests.post(
                    GROQ_ENDPOINT,
                    headers=headers,
                    json=payload,
                    timeout=8,
                )
                if response.status_code == 200:
                    data = response.json()
                    content = (
                        data.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "")
                        .strip()
                    )
                    if content:
                        return content
            except Exception as exc:
                import sys
                print(f"Groq LLM text call error ({model_name}): {exc}", file=sys.stderr)

    gemini_key = _get_env_key("GEMINI_API_KEY")
    gemini_model = _get_env_key("GEMINI_MODEL", "gemini-1.5-flash")
    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent?key={gemini_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.4, "maxOutputTokens": 300},
            }
            response = requests.post(url, json=payload, timeout=8)
            if response.status_code == 200:
                data = response.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts and "text" in parts[0]:
                        text = parts[0]["text"].strip()
                        if text:
                            return text
        except Exception as exc:
            import sys
            print(f"Gemini LLM API Call Error: {exc}", file=sys.stderr)

    return fallback_text
