from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.risk_threshold import RiskThreshold
from app.models.crop_variety import CropVariety
from app.models.ndvi_cache import NDVICache


# Regional agricultural climate zones in Bangladesh
SALINE_BELT_REGIONS = ["Khulna", "Barishal", "Satkhira", "Patuakhali", "Barguna", "Bagerhat", "Bhola"]
DROUGHT_PRONE_REGIONS = ["Rajshahi", "Rangpur", "Dinajpur", "Bogura", "Naogaon", "Kushtia", "Pabna"]
HAOR_FLOOD_REGIONS = ["Sylhet", "Sunamganj", "Netrokona", "Kishoreganj", "Habiganj", "Moulvibazar"]


def calculate_risk_and_alerts(
    crop: str,
    region: str,
    variety_code: str,
    predicted_yield: float,
    lower_bound: float,
    upper_bound: float,
    cropping_type: str = "single",
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    """
    Evaluates agricultural risk and threshold detection based on:
    1. Predicted yield vs crop risk thresholds in database
    2. Variety specific stress tolerances vs regional climate vulnerabilities
    3. Satellite NDVI canopy index for the target region
    4. Prediction uncertainty band (lower bound spread)
    """
    risk_score = 25.0  # Base healthy baseline
    risk_factors: List[str] = []
    alerts: List[Dict[str, Any]] = []

    # 1. Fetch Thresholds from DB or agronomic defaults
    yield_threshold = None
    if db:
        yield_threshold = (
            db.query(RiskThreshold)
            .filter(
                RiskThreshold.crop.ilike(crop.strip()),
                RiskThreshold.metric == "predicted_yield_min",
            )
            .first()
        )

    # Defaults if DB doesn't have custom record
    low_thresh = yield_threshold.low_threshold if yield_threshold else 4.2
    med_thresh = yield_threshold.medium_threshold if yield_threshold else 3.4
    high_thresh = yield_threshold.high_threshold if yield_threshold else 2.8

    # Yield deficit evaluation
    if predicted_yield < high_thresh:
        risk_score += 45.0
        risk_factors.append(f"পূর্বাভাসকৃত ফলন চরম সীমার নিচে ({predicted_yield:.2f} < {high_thresh:.2f} টন/হেক্টর)")
        alerts.append({
            "id": "alert-yield-critical",
            "category": "yield",
            "level": "high",
            "title": f"চরম ফলন ঘাটতি ঝুঁকি ({crop})",
            "title_bn": f"চরম ফলন ঘাটতি ঝুঁকি ({crop})",
            "title_en": f"Critical Yield Deficit Risk ({crop})",
            "description": f"{region} অঞ্চলে {crop} ফসলের সম্ভাব্য ফলন স্বাভাবিকের চেয়ে অনেক কম। দ্রুত মাটি পরীক্ষা ও নিবিড় পরিচর্যা প্রয়োজন।",
            "description_bn": f"{region} অঞ্চলে {crop} ফসলের সম্ভাব্য ফলন স্বাভাবিকের চেয়ে অনেক কম। দ্রুত মাটি পরীক্ষা ও নিবিড় পরিচর্যা প্রয়োজন।",
            "description_en": f"Forecast yield in {region} falls critically below agronomic normal ({predicted_yield:.2f} ton/ha).",
            "action_bn": "অবিলম্বে উপ-সহকারী কৃষি কর্মকর্তার পরামর্শে বিশেষ পুষ্টি ও সেচ ব্যবস্থাপনা গ্রহণ করুন।",
            "action_en": "Consult local sub-assistant agriculture officer immediately for emergency remediation.",
        })
    elif predicted_yield < med_thresh:
        risk_score += 25.0
        risk_factors.append(f"পূর্বাভাসকৃত ফলন মাঝারি সতর্কতার নিচে ({predicted_yield:.2f} < {med_thresh:.2f} টন/হেক্টর)")
        alerts.append({
            "id": "alert-yield-moderate",
            "category": "yield",
            "level": "medium",
            "title": f"মাঝারি ফলন সতর্কতা",
            "title_bn": f"মাঝারি ফলন সতর্কতা",
            "title_en": f"Moderate Yield Alert",
            "description": f"কাঙ্ক্ষিত ফলন অর্জনে পরিমিত সার ও সময়মতো আগাছা পরিষ্কার করা আবশ্যক।",
            "description_bn": f"কাঙ্ক্ষিত ফলন অর্জনে পরিমিত সার ও সময়মতো আগাছা পরিষ্কার করা আবশ্যক।",
            "description_en": f"Forecast yield indicates moderate shortfall. Timely weeding and top-dressing required.",
            "action_bn": "শতক প্রতি অতিরিক্ত ২৫০ গ্রাম পটাশ ও ইউরিয়া প্রয়োগ নিশ্চিত করুন।",
            "action_en": "Ensure balanced top-dressing of nitrogen and potash per decimal.",
        })

    # 2. Uncertainty Band (Lower bound gap)
    if predicted_yield > 0:
        spread_pct = ((predicted_yield - lower_bound) / predicted_yield) * 100.0
        if spread_pct > 18.0:
            risk_score += 15.0
            risk_factors.append(f"আবহাওয়া অনিশ্চয়তা বা সম্ভাব্য অস্থিরতা ({spread_pct:.1f}% নিম্নমুখী ঝুঁকি)")
            alerts.append({
                "id": "alert-uncertainty-spread",
                "category": "climate",
                "level": "medium",
                "title": "আবহাওয়া ও জলবায়ু অনিশ্চয়তা ঝুঁকি",
                "title_bn": "আবহাওয়া ও জলবায়ু অনিশ্চয়তা ঝুঁকি",
                "title_en": "Climate & Downside Uncertainty Alert",
                "description": f"আঞ্চলিক জলবায়ু ও বৃষ্টিপাতের তারতম্যের কারণে ফলনে {lower_bound:.2f} টন/হেক্টর পর্যন্ত নিম্নমুখী বিচ্যুতি ঘটতে পারে।",
                "description_bn": f"আঞ্চলিক জলবায়ু ও বৃষ্টিপাতের তারতম্যের কারণে ফলনে {lower_bound:.2f} টন/হেক্টর পর্যন্ত নিম্নমুখী বিচ্যুতি ঘটতে পারে।",
                "description_en": f"Historical weather variance implies potential downward deviation to {lower_bound:.2f} ton/ha.",
                "action_bn": "আবহাওয়ার পূর্বাভাস নিয়মিত পর্যবেক্ষণ করুন এবং আকস্মিক বৃষ্টি বা খরার পূর্বে সুরক্ষা নিন।",
                "action_en": "Monitor local weather forecasts closely before scheduling pesticide or fertilizer sprays.",
            })

    # 3. Variety Parameter Integration & Geographic Vulnerabilities
    variety_obj = None
    if db:
        variety_obj = (
            db.query(CropVariety)
            .filter(
                CropVariety.crop.ilike(crop.strip()),
                (CropVariety.variety_code.ilike(variety_code.strip()) | CropVariety.name_en.ilike(f"%{variety_code.strip()}%")),
            )
            .first()
        )

    variety_type = variety_obj.variety_type if variety_obj else ("Local" if "local" in variety_code.lower() else "HYV")
    stress_tolerance = variety_obj.stress_tolerance if variety_obj else "Standard"

    # Salinity mismatch alert
    is_coastal = any(r.lower() in region.lower() for r in SALINE_BELT_REGIONS)
    if is_coastal and stress_tolerance != "Saline":
        risk_score += 20.0
        risk_factors.append(f"উপকূলীয় লবণাক্ত অঞ্চলে সাধারণ জাতের আবাদ ({variety_code})")
        alerts.append({
            "id": "alert-salinity-vulnerability",
            "category": "variety",
            "level": "high",
            "title": "উপকূলীয় মাটির লবণাক্ততা ঝুঁকি",
            "title_bn": "উপকূলীয় মাটির লবণাক্ততা ঝুঁকি",
            "title_en": "Coastal Salinity Mismatch Alert",
            "description": f"{region} একটি লবণাক্ত প্রবণ অঞ্চল। নির্বাচিত জাতটি ({variety_code}) উচ্চ লবণাক্ততা প্রতিরোধী না হওয়ায় শিকড় ক্ষতিগ্রস্ত হতে পারে।",
            "description_bn": f"{region} একটি লবণাক্ত প্রবণ অঞ্চল। নির্বাচিত জাতটি ({variety_code}) উচ্চ লবণাক্ততা প্রতিরোধী না হওয়ায় শিকড় ক্ষতিগ্রস্ত হতে পারে।",
            "description_en": f"{region} experiences seasonal soil salinity. Non-tolerant variety may suffer osmotic stress.",
            "action_bn": "ব্রি ধান৬৭ বা লবণাক্ত সহনশীল জাত নির্বাচন করুন এবং মিষ্টি পানির সেচ নিশ্চিত করুন।",
            "action_en": "Switch to certified salt-tolerant variety (e.g. BRRI dhan67) and irrigate with fresh water.",
        })

    # Drought mismatch alert
    is_drought_zone = any(r.lower() in region.lower() for r in DROUGHT_PRONE_REGIONS)
    if is_drought_zone and stress_tolerance != "Drought" and crop.lower() in ["rice", "wheat"]:
        risk_score += 15.0
        risk_factors.append(f"বরেন্দ্র/উত্তরাঞ্চলের খরা প্রবণ অঞ্চলে সেচ সংকট ঝুঁকি")
        alerts.append({
            "id": "alert-drought-irrigation",
            "category": "moisture",
            "level": "medium",
            "title": "মাটির আর্দ্রতা ঘাটতি ও সেচ সতর্কতা",
            "title_bn": "মাটির আর্দ্রতা ঘাটতি ও সেচ সতর্কতা",
            "title_en": "Moisture Deficit & Irrigation Alert",
            "description": f"{region} অঞ্চলে ভূগর্ভস্থ পানির স্তর দ্রুত নামতে পারে। ফুল আসার সময় পানির অভাব হলে দানা চিটা হতে পারে।",
            "description_bn": f"{region} অঞ্চলে ভূগর্ভস্থ পানির স্তর দ্রুত নামতে পারে। ফুল আসার সময় পানির অভাব হলে দানা চিটা হতে পারে।",
            "description_en": f"Barind/Northern belt prone to water table stress. Water shortage during flowering causes unfilled grains.",
            "action_bn": "এডব্লিউডি (AWD - পর্যায়ক্রমে ভিজানো ও শুকানো) পদ্ধতিতে সাশ্রয়ী সেচ নিশ্চিত করুন।",
            "action_en": "Adopt Alternate Wetting and Drying (AWD) irrigation technology.",
        })

    # Flash flood / Haor alert
    is_haor = any(r.lower() in region.lower() for r in HAOR_FLOOD_REGIONS)
    if is_haor and crop.lower() == "rice":
        alerts.append({
            "id": "alert-haor-early-flood",
            "category": "climate",
            "level": "medium",
            "title": "হাওর অঞ্চলে আগাম পাহাড়ি ঢলের সতর্কতা",
            "title_bn": "হাওর অঞ্চলে আগাম পাহাড়ি ঢলের সতর্কতা",
            "title_en": "Early Haor Flash-Flood Caution",
            "description": f"{region} অঞ্চলে বৈশাখ মাসে আগাম পাহাড়ি ঢলের ঝুঁকি থাকে। স্বল্পমেয়াদী জাত আবাদ করে আগাম কর্তন জরুরি।",
            "description_bn": f"{region} অঞ্চলে বৈশাখ মাসে আগাম পাহাড়ি ঢলের ঝুঁকি থাকে। স্বল্পমেয়াদী জাত আবাদ করে আগাম কর্তন জরুরি।",
            "description_en": f"Haor belt vulnerable to flash floods from upstream. Timely harvesting is critical.",
            "action_bn": "ধানের ৮০% সোনালী রং ধারণ করলেই দ্রুত কেটে নিরাপদ স্থানে সংরক্ষণ করুন।",
            "action_en": "Harvest when 80% of grains reach golden maturity to preempt flood inundation.",
        })

    # 4. Satellite NDVI Health check
    ndvi_val = None
    veg_status = "স্বাভাবিক"
    if db:
        try:
            ndvi_entry = (
                db.query(NDVICache)
                .filter(NDVICache.region_name.ilike(region.strip()))
                .order_by(NDVICache.computed_at.desc())
                .first()
            )
            if ndvi_entry and ndvi_entry.ndvi_value is not None:
                ndvi_val = ndvi_entry.ndvi_value
                veg_status = ndvi_entry.vegetation_status or "স্বাভাবিক"
        except Exception:
            pass

    if ndvi_val is not None:
        if ndvi_val < 0.32:
            risk_score += 20.0
            risk_factors.append(f"স্যাটেলাইট চিত্রে ফসলের ক্যানোপি অত্যন্ত দুর্বল (NDVI {ndvi_val:.2f})")
            alerts.append({
                "id": "alert-ndvi-stunted",
                "category": "pest",
                "level": "high",
                "title": "দুর্বল ভেজিটেশন ও রোগবালাই ঝুঁকি (Satellite NDVI)",
                "title_bn": "দুর্বল ভেজিটেশন ও রোগবালাই ঝুঁকি (Satellite NDVI)",
                "title_en": "Low Vegetation Index & Pest/Disease Risk",
                "description": f"উপগ্রহ চিত্রে {region} অঞ্চলের শস্যক্ষেত্রে স্বাভাবিকের চেয়ে কম সবুজ পাতার ঘনত্ব (NDVI: {ndvi_val:.2f}) ধরা পড়েছে। পাতা পোড়া বা শিকড় পচা রোগ হতে পারে।",
                "description_bn": f"উপগ্রহ চিত্রে {region} অঞ্চলের শস্যক্ষেত্রে স্বাভাবিকের চেয়ে কম সবুজ পাতার ঘনত্ব (NDVI: {ndvi_val:.2f}) ধরা পড়েছে। পাতা পোড়া বা শিকড় পচা রোগ হতে পারে।",
                "description_en": f"Satellite imagery detects thin canopy cover (NDVI: {ndvi_val:.2f}) indicating stunted biomass or pest damage.",
                "action_bn": "জমির পাতা পরীক্ষা করে শীথ ব্লাইট বা ব্লাস্টের উপস্থিতি নিশ্চিত করুন এবং জিংক/সালফার প্রয়োগ করুন।",
                "action_en": "Inspect leaves for fungal blight/blast; supplement with micronutrient zinc and sulfur.",
            })

    # 5. Crop-specific default pest alert if none generated yet
    if not any(a["category"] == "pest" for a in alerts):
        pest_title_map = {
            "Rice": ("মাজরা পোকা ও নেক ব্লাস্ট পর্যবেক্ষণ", "Stem Borer & Neck Blast Vigilance"),
            "Wheat": ("গম ব্লাস্ট ও মরিচা রোগ সতর্কতা", "Wheat Blast & Rust Vigilance"),
            "Potato": ("লেট ব্লাইট (নাবি ধসা) রোগ সতর্কতা", "Late Blight Vigilance"),
            "Maize": ("ফল আর্মিওয়ার্ম পোকা আক্রমণ পর্যবেক্ষণ", "Fall Armyworm Alert"),
            "Mustard": ("জাবপোকা (এফিড) আক্রমণ সতর্কতা", "Mustard Aphid Alert"),
            "Jute": ("বিছা পোকা ও হলুদ মাকড় পর্যবেক্ষণ", "Jute Hairy Caterpillar Alert"),
        }
        title_bn, title_en = pest_title_map.get(crop, (f"{crop} সাধারণ বালাই সতর্কতা", f"{crop} Pest Vigilance"))
        alerts.append({
            "id": "alert-general-pest",
            "category": "pest",
            "level": "low",
            "title": title_bn,
            "title_bn": title_bn,
            "title_en": title_en,
            "description": f"আবহাওয়ার পরিবর্তনের ফলে হালকা বালাইয়ের সম্ভাবনা রয়েছে। আলোর ফাঁদ ব্যবহার করুন।",
            "description_bn": f"আবহাওয়ার পরিবর্তনের ফলে হালকা বালাইয়ের সম্ভাবনা রয়েছে। আলোর ফাঁদ ব্যবহার করুন।",
            "description_en": "Seasonal atmospheric humidity may harbor minor pest infestations. Install light traps.",
            "action_bn": "সপ্তাহে দুই দিন সকালে ফসল পরিদর্শন করুন এবং প্রয়োজনে জৈব বালাইনাশক ব্যবহার করুন।",
            "action_en": "Scout fields twice weekly in morning hours; use biological control where possible.",
        })

    # Final Risk Level Determination
    risk_score = min(max(round(risk_score, 1), 5.0), 98.0)
    if risk_score >= 65.0:
        risk_level = "high"
    elif risk_score >= 40.0:
        risk_level = "medium"
    else:
        risk_level = "low"

    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "risk_factors": risk_factors,
        "alerts": alerts,
        "ndvi_context": {
            "value": ndvi_val,
            "status": veg_status,
        },
    }
