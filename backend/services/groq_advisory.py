import os
import json
from dotenv import load_dotenv
from models import Variety
from schemas import WeatherScenario, RiskEvaluationResult
from groq import Groq

load_dotenv()

def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY", "")
    if api_key:
        try:
            return Groq(api_key=api_key)
        except Exception:
            return None
    return None

def generate_fallback_bangla_advisory(variety: Variety, eval_result: RiskEvaluationResult) -> dict:
    """
    Generates deterministic, highly practical Bangla agricultural advisory
    when Groq API key is omitted or service is unavailable.
    """
    risk_level = eval_result.risk_level
    scenario = eval_result.scenario

    action_items = []
    irrigation_advice = ""
    pest_advice = ""

    # Irrigation Advice
    if scenario.rainfall < variety.rainfall_min_mm:
        irrigation_advice = (
            f"ক্ষেতে পর্যাপ্ত রসের অভাব রয়েছে (বৃষ্টিপাত {scenario.rainfall} মিমি)। "
            f"{variety.name_bangla} জাতের জন্য ৩-৫ সেমি হালকা সেচ অবিলম্বে নিশ্চিত করুন। "
            "বিকালে সেচ দেওয়া সবচেয়ে কার্যকরী।"
        )
        action_items.append("ক্ষেতে জরুরি হালকা সেচের ব্যবস্থা করুন।")
    elif scenario.rainfall > variety.rainfall_max_mm:
        irrigation_advice = (
            f"অতিরিক্ত বৃষ্টিপাতের কারণে (বৃষ্টিপাত {scenario.rainfall} মিমি) জলবদ্ধতা তৈরি হতে পারে। "
            "ক্ষেত থেকে বাড়তি পানি দ্রুত নিষ্কাশনের জন্য নালার ব্যবস্থা বজায় রাখুন।"
        )
        action_items.append("ক্ষেতের অতিরিক্ত পানি নিষ্কাশনের ব্যবস্থা রাখুন।")
    else:
        irrigation_advice = "মাটিতে স্বাভাবিক সেচ পরিস্থিতি বজায় রাখুন। অতিরিক্ত সেচ দেওয়ার প্রয়োজন নেই।"
        action_items.append("মাটিতে প্রয়োজনীয় আদ্রতা নিয়মিত পর্যবেক্ষণ করুন।")

    # Pest Advice
    if eval_result.metric_levels.get("pest_density") in ["HIGH", "CRITICAL"] or scenario.humidity > 80:
        pest_advice = (
            f"উচ্চ আর্দ্রতা ({scenario.humidity}%) ও পোকার ঘনত্বের কারণে ব্লাস্ট রোগ ও বাদামী গাছফড়িং (কারেন্ট পোকা) "
            "আক্রমণের সম্ভাবনা রয়েছে। প্রতি লিটার পানিতে ট্রাইসাইক্লাজল/আইসোপ্রোথিওলেন বা সঠিক বালাইনাশক নিয়ম অনুযায়ী স্প্রে করুন।"
        )
        action_items.append("অনুমোদিত বালাইনাশক দিয়ে স্প্রে করুন ও আলো ফাঁদ ব্যবহার করুন।")
    else:
        pest_advice = "বর্তমানে বালাই ঝুঁকি সহনশীল মাত্রায় আছে। নিয়মিত শতকরা ৫টি আলো ফাঁদ বসিয়ে পর্যবেক্ষণ করুন।"
        action_items.append("সকালে ও বিকালে মাঠ ঘুরে শস্যের পাতা পর্যবেক্ষণ করুন।")

    # General Advisory Text
    if risk_level == "CRITICAL":
        advisory_text = (
            f"জরুরী কৃষি পূর্বাভাস ({variety.name_bangla}): আবহাওয়া পরিস্থিতি অত্যন্ত ঝুঁকিপূর্ণ! "
            f"তাপমাত্রা {scenario.temperature}°C ও বৃষ্টিপাত {scenario.rainfall} মিমি। "
            "ফসল রক্ষায় অবিলম্বে নিচের পদক্ষেপসমূহ গ্রহণ করুন।"
        )
    elif risk_level == "HIGH":
        advisory_text = (
            f"সতর্কতা পরামর্শ ({variety.name_bangla}): আবহাওয়ার প্রতিকূলতার কারণে ফসলে উচ্চ ঝুঁকির সম্ভাবনা রয়েছে। "
            "বিশেষ করে সেচ ও বালাই ব্যবস্থাপনায় নজর দেওয়া জরুরি।"
        )
    elif risk_level == "MEDIUM":
        advisory_text = (
            f"সাধারণ পর্যবেক্ষণ পরামর্শ ({variety.name_bangla}): ফসল সার্বিকভাবে ভালো হলেও আর্দ্রতা ও তাপমাত্রার সামান্য তারতম্য রয়েছে। "
            "নিয়মিত যত্ন নিন।"
        )
    else:
        advisory_text = (
            f"অনুকূল আবহাওয়া পরামর্শ ({variety.name_bangla}): আবহাওয়ার সার্বিক পরিস্থিতি অনুকূল। "
            "সঠিক সময়মতো সুষম সার ও হালকা পর্যবেক্ষণ বজায় রাখুন।"
        )

    return {
        "advisory_text_bn": advisory_text,
        "action_items_bn": action_items,
        "irrigation_advice_bn": irrigation_advice,
        "pest_advice_bn": pest_advice,
        "llm_provider": "Rule-Engine Local Fallback"
    }


def generate_bangla_advisory(variety: Variety, eval_result: RiskEvaluationResult) -> dict:
    client = get_groq_client()
    if not client:
        return generate_fallback_bangla_advisory(variety, eval_result)

    system_prompt = (
        "You are FieldForesight AI, an expert agricultural scientist and agronomist in Bangladesh. "
        "Your task is to generate actionable, empathetic, accurate agricultural advisory in proper natural Bangla (বাংলা). "
        "Return ONLY a valid JSON object matching this structure:\n"
        "{\n"
        '  "advisory_text_bn": "...",\n'
        '  "action_items_bn": ["...", "..."],\n'
        '  "irrigation_advice_bn": "...",\n'
        '  "pest_advice_bn": "..."\n'
        "}"
    )

    user_prompt = f"""
ফসল/জাত: {variety.name_bangla} ({variety.name})
জাতের বৈশিষ্ট্য: আদর্শ তাপমাত্রা {variety.optimal_temp_min}°C - {variety.optimal_temp_max}°C, বৃষ্টিপাত {variety.rainfall_min_mm}-{variety.rainfall_max_mm} মিমি, বালাই সংবেদনশীলতা: {variety.pest_susceptibility}।

বর্তমান পূর্বাভাস পরিস্থিতি:
- সামগ্রিক ঝুঁকি স্তর: {eval_result.risk_level} (স্কোর: {eval_result.overall_risk_score}/100)
- তাপমাত্রা: {eval_result.scenario.temperature}°C (ঝুঁকি: {eval_result.metric_levels['temperature']})
- বৃষ্টিপাত: {eval_result.scenario.rainfall} মিমি (ঝুঁকি: {eval_result.metric_levels['rainfall']})
- আর্দ্রতা: {eval_result.scenario.humidity}% (ঝুঁকি: {eval_result.metric_levels['humidity']})
- বাতাসের গতি: {eval_result.scenario.wind_speed} কিমি/ঘণ্টা
- পোকার ঘনত্ব: {eval_result.scenario.pest_density} পোকা/মি²

সনাক্তকৃত সসংকেতসমূহ:
{json.dumps(eval_result.triggered_warnings, ensure_ascii=False)}

কৃষকদের জন্য স্পষ্ট, বাস্তবসম্মত বাংলা কৃষি পরামর্শ ও ৩টি সুনির্দিষ্ট পদক্ষেপ তৈরি করুন।
"""

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.4,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        parsed = json.loads(content)
        parsed["llm_provider"] = "Groq Llama-3.3 70B"
        return parsed
    except Exception as e:
        print(f"Groq API Error: {e}. Switching to rule fallback.")
        return generate_fallback_bangla_advisory(variety, eval_result)
