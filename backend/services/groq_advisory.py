import os
import json
import logging
from dotenv import load_dotenv
from models import Variety
from schemas import WeatherScenario, RiskEvaluationResult
from groq import Groq

load_dotenv()
logger = logging.getLogger(__name__)


def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY", "")
    if api_key:
        try:
            return Groq(api_key=api_key)
        except Exception as err:
            logger.warning("Failed to initialize Groq client: %s", err)
            return None
    return None


def generate_fallback_bangla_advisory(variety: Variety, eval_result: RiskEvaluationResult) -> dict:
    risk_level = eval_result.risk_level
    scenario = eval_result.scenario

    action_items = []
    irrigation_advice = ""
    pest_advice = ""

    if scenario.rainfall < variety.rainfall_min_mm:
        irrigation_advice = (
            f"Soil moisture is deficient (Rainfall: {scenario.rainfall} mm). "
            f"Apply 3-5 cm light irrigation promptly for {variety.name}. "
            "Late afternoon irrigation is highly recommended to minimize evaporation loss."
        )
        action_items.append("Schedule immediate light irrigation during late afternoon.")
    elif scenario.rainfall > variety.rainfall_max_mm:
        irrigation_advice = (
            f"Excessive rainfall detected (Rainfall: {scenario.rainfall} mm), presenting high risk of waterlogging. "
            "Ensure field drainage channels and trenches are fully cleared for rapid water evacuation."
        )
        action_items.append("Clear drainage canals to prevent waterlogging around roots.")
    else:
        irrigation_advice = "Maintain normal soil moisture levels. Additional supplemental irrigation is not required."
        action_items.append("Monitor soil moisture levels regularly.")

    if eval_result.metric_levels.get("pest_density") in ["HIGH", "CRITICAL"] or scenario.humidity > 80:
        pest_advice = (
            f"Elevated humidity ({scenario.humidity}%) and pest density indicate increased vulnerability to fungal blast and brown planthopper (BPH). "
            "Apply recommended agronomic fungicides/insecticides (e.g. Tricyclazole/Isoprothiolane) according to safety standards."
        )
        action_items.append("Spray approved agrochemicals and install light traps across the plot.")
    else:
        pest_advice = "Pest risk is currently within manageable thresholds. Set up 5 light traps per hectare for active surveillance."
        action_items.append("Conduct regular field scouting in early morning and late afternoon.")

    if risk_level == "CRITICAL":
        advisory_text = (
            f"CRITICAL ADVISORY ({variety.name}): Weather conditions are severely unfavorable! "
            f"Temperature is {scenario.temperature}°C and rainfall is {scenario.rainfall} mm. "
            "Take urgent agronomic measures immediately to mitigate crop damage."
        )
    elif risk_level == "HIGH":
        advisory_text = (
            f"HIGH RISK ALERT ({variety.name}): Unfavorable weather trends indicate elevated stress on crops. "
            "Prioritize soil drainage/irrigation and disease management."
        )
    elif risk_level == "MEDIUM":
        advisory_text = (
            f"MODERATE RISK ADVISORY ({variety.name}): Crop growth is stable, though slight temperature and humidity variations require active field monitoring."
        )
    else:
        advisory_text = (
            f"OPTIMAL CONDITION ADVISORY ({variety.name}): Overall weather conditions are favorable and supportive of crop development. "
            "Maintain balanced fertilization and regular field inspections."
        )

    return {
        "advisory_text_bn": advisory_text,
        "action_items_bn": action_items,
        "irrigation_advice_bn": irrigation_advice,
        "pest_advice_bn": pest_advice,
        "llm_provider": "Rule Engine Fallback"
    }


def generate_bangla_advisory(variety: Variety, eval_result: RiskEvaluationResult) -> dict:
    client = get_groq_client()
    if not client:
        return generate_fallback_bangla_advisory(variety, eval_result)

    system_prompt = (
        "You are FieldForesight AI, an expert agricultural scientist and agronomist. "
        "Your task is to generate actionable, empathetic, scientifically rigorous agricultural advisory in clear, professional English. "
        "Return ONLY a valid JSON object matching this structure:\n"
        "{\n"
        '  "advisory_text_bn": "...",\n'
        '  "action_items_bn": ["...", "..."],\n'
        '  "irrigation_advice_bn": "...",\n'
        '  "pest_advice_bn": "..."\n'
        "}"
    )

    user_prompt = f"""
Crop / Variety: {variety.name} ({variety.crop_type})
Variety Traits: Optimal Temp {variety.optimal_temp_min}°C - {variety.optimal_temp_max}°C, Rainfall {variety.rainfall_min_mm}-{variety.rainfall_max_mm} mm, Pest Susceptibility: {variety.pest_susceptibility}.

Current Simulation Scenario:
- Overall Risk Level: {eval_result.risk_level} (Score: {eval_result.overall_risk_score}/100)
- Temperature: {eval_result.scenario.temperature}°C (Risk: {eval_result.metric_levels['temperature']})
- Rainfall: {eval_result.scenario.rainfall} mm (Risk: {eval_result.metric_levels['rainfall']})
- Humidity: {eval_result.scenario.humidity}% (Risk: {eval_result.metric_levels['humidity']})
- Wind Speed: {eval_result.scenario.wind_speed} km/h
- Pest Density: {eval_result.scenario.pest_density} pests/m²

Detected Warnings:
{json.dumps(eval_result.triggered_warnings, ensure_ascii=False)}

Generate a clear, authoritative English agronomic advisory with 2-3 specific action items, irrigation instructions, and pest management guidance.
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
        content = response.choices[0].message.content.strip()
        # Clean potential markdown wrapping (e.g. ```json ... ```)
        if content.startswith("```"):
            lines = content.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            content = "\n".join(lines).strip()

        parsed = json.loads(content)
        parsed["llm_provider"] = "Groq Llama-3.3 70B"
        return parsed
    except Exception as err:
        logger.error("Groq API error during advisory generation: %s", err)
        return generate_fallback_bangla_advisory(variety, eval_result)
