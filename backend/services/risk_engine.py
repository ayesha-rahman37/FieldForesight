from models import Variety, RiskThreshold
from schemas import WeatherScenario, RiskEvaluationResult

def evaluate_metric_risk(val: float, low_max: float, med_max: float, high_max: float) -> tuple[float, str]:
    """
    Returns (risk_score_0_100, risk_level_str)
    """
    if val <= low_max:
        score = (val / low_max) * 25.0 if low_max > 0 else 10.0
        return min(max(score, 5.0), 25.0), "LOW"
    elif val <= med_max:
        range_span = max(med_max - low_max, 0.1)
        score = 25.0 + ((val - low_max) / range_span) * 25.0
        return min(max(score, 25.0), 50.0), "MEDIUM"
    elif val <= high_max:
        range_span = max(high_max - med_max, 0.1)
        score = 50.0 + ((val - med_max) / range_span) * 25.0
        return min(max(score, 50.0), 75.0), "HIGH"
    else:
        # Critical risk
        excess = val - high_max
        score = 75.0 + min(excess * 5.0, 25.0)
        return min(score, 100.0), "CRITICAL"


def evaluate_risk(variety: Variety, scenario: WeatherScenario, custom_thresholds: list[RiskThreshold] = None) -> RiskEvaluationResult:
    # Default thresholds derived from Variety parameters if no explicit RiskThreshold entry
    temp_low = variety.optimal_temp_min
    temp_med = variety.optimal_temp_max
    temp_high = variety.max_temp_threshold

    rain_low = variety.rainfall_min_mm
    rain_med = (variety.rainfall_min_mm + variety.rainfall_max_mm) / 2.0
    rain_high = variety.rainfall_max_mm

    # Pest multiplier based on variety susceptibility
    pest_susceptibility_mult = {
        "Low": 0.8,
        "Medium": 1.0,
        "High": 1.3
    }.get(variety.pest_susceptibility, 1.0)

    # 1. Temperature Risk
    temp_score, temp_level = evaluate_metric_risk(scenario.temperature, temp_low, temp_med, temp_high)
    if scenario.temperature < temp_low - 5.0:
        # Cold stress
        temp_score = min(75.0, temp_score + 35.0)
        temp_level = "HIGH" if temp_score < 80 else "CRITICAL"

    # 2. Rainfall / Drought Risk
    if scenario.rainfall < variety.rainfall_min_mm * 0.4:
        rain_score, rain_level = 85.0, "CRITICAL"  # Severe drought
    elif scenario.rainfall < variety.rainfall_min_mm:
        rain_score, rain_level = 60.0, "HIGH"      # Moderate drought
    elif scenario.rainfall > variety.rainfall_max_mm * 1.5:
        rain_score, rain_level = 88.0, "CRITICAL"  # Excessive flooding
    elif scenario.rainfall > variety.rainfall_max_mm:
        rain_score, rain_level = 65.0, "HIGH"      # Heavy rainfall
    else:
        rain_score, rain_level = 15.0, "LOW"

    # 3. Humidity Risk (High humidity > 85% increases fungal blast risk)
    if scenario.humidity > 85.0:
        hum_score, hum_level = 75.0, "HIGH"
    elif scenario.humidity > 75.0:
        hum_score, hum_level = 45.0, "MEDIUM"
    else:
        hum_score, hum_level = 15.0, "LOW"

    # 4. Pest Risk
    effective_pest = scenario.pest_density * pest_susceptibility_mult
    pest_score, pest_level = evaluate_metric_risk(effective_pest, 10.0, 25.0, 40.0)

    # 5. Wind Risk
    if scenario.wind_speed > 35.0:
        wind_score, wind_level = 85.0, "CRITICAL"
    elif scenario.wind_speed > 25.0:
        wind_score, wind_level = 60.0, "HIGH"
    else:
        wind_score, wind_level = 15.0, "LOW"

    # Weighted overall score
    overall_score = round(
        0.30 * temp_score +
        0.25 * rain_score +
        0.20 * pest_score +
        0.15 * hum_score +
        0.10 * wind_score, 1
    )

    if overall_score >= 75.0:
        overall_level = "CRITICAL"
    elif overall_score >= 50.0:
        overall_level = "HIGH"
    elif overall_score >= 25.0:
        overall_level = "MEDIUM"
    else:
        overall_level = "LOW"

    # Triggered Warnings in Bangla
    warnings = []
    if temp_level in ["HIGH", "CRITICAL"]:
        if scenario.temperature > temp_high:
            warnings.append(f"উচ্চ তাপমাত্রা সসংকেত: {scenario.temperature}°C (সহনশীলতা {temp_high}°C এর বেশি)")
        else:
            warnings.append(f"নিম্ন তাপমাত্রা সংকেত: {scenario.temperature}°C (আদর্শ সর্বনিম্ন {temp_low}°C)")

    if rain_level in ["HIGH", "CRITICAL"]:
        if scenario.rainfall < variety.rainfall_min_mm:
            warnings.append(f"খরা ঝুঁকি সসংকেত: বৃষ্টিপাত {scenario.rainfall} মিমি (প্রয়োজনীয় ন্যূনতম {variety.rainfall_min_mm} মিমি)")
        else:
            warnings.append(f"অতিবৃষ্টি/প্লাবন সংকেত: বৃষ্টিপাত {scenario.rainfall} মিমি (সর্বোচ্চ সহনশীলতা {variety.rainfall_max_mm} মিমি)")

    if pest_level in ["HIGH", "CRITICAL"]:
        warnings.append(f"বালাই আক্রমণ ঝুঁকি: পোকার ঘনত্ব {scenario.pest_density}/মি² (জাতের অতিসংবেদনশীলতা: {variety.pest_susceptibility})")

    if hum_level in ["HIGH", "CRITICAL"]:
        warnings.append(f"উচ্চ আর্দ্রতা সতর্কতা: {scenario.humidity}% (ছত্রাকজনিত ব্লাস্ট রোগের উচ্চ ঝুঁকি)")

    if wind_level in ["HIGH", "CRITICAL"]:
        warnings.append(f"তীব্র বাতাস সতর্কতা: {scenario.wind_speed} কিমি/ঘণ্টা (ধান হেলে পড়ার বা শস্য ক্ষতির সম্ভাবনা)")

    if not warnings:
        warnings.append("আবহাওয়া পরিস্থিতি স্বাভাবিক ও অনুকূল রয়েছে।")

    return RiskEvaluationResult(
        variety_id=variety.id,
        variety_name=variety.name,
        variety_name_bangla=variety.name_bangla,
        risk_level=overall_level,
        overall_risk_score=overall_score,
        metric_scores={
            "temperature": round(temp_score, 1),
            "rainfall": round(rain_score, 1),
            "humidity": round(hum_score, 1),
            "pest_density": round(pest_score, 1),
            "wind_speed": round(wind_score, 1)
        },
        metric_levels={
            "temperature": temp_level,
            "rainfall": rain_level,
            "humidity": hum_level,
            "pest_density": pest_level,
            "wind_speed": wind_level
        },
        triggered_warnings=warnings,
        scenario=scenario
    )
