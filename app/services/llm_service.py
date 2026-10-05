import os
import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3.8-flash"
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent"


def generate_llm_text(prompt: str, fallback_text: str) -> str:
    """
    Calls Google Gemini LLM API (gemini-3.8-flash) using GEMINI_API_KEY from .env.
    Falls back gracefully to fallback_text if key is missing or call fails.
    """
    api_key = os.getenv("GEMINI_API_KEY") or GEMINI_API_KEY
    if not api_key:
        return fallback_text

    try:
        url = f"{GEMINI_ENDPOINT}?key={api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 300,
            }
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
    except Exception as e:
        print(f"Gemini LLM API Call Error: {e}")

    return fallback_text
