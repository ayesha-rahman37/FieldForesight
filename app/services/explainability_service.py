"""
Explainability service.

Computes contextual environmental factor contributions from real system data:

1. Look up the prediction record in PredictionHistory using prediction_id
   to retrieve the actual crop and region.

2. Query weather data from app/data/weather_daily.csv (or weather_yearly.csv)
   for the prediction's region.

3. Query the NDVICache table for the prediction's region to get current
   vegetation status and NDVI index.

4. Calculate normalized factor contributions (summing to 100%) based on min-max
   scaling of real environmental observations (rainfall, temperature, and NDVI/soil).

5. Generate an honestly framed contextual summary text in Bengali explaining
   the environmental observations for the region without making false causal claims.
"""

import os
import pandas as pd
from sqlalchemy.orm import Session

from app.schemas.explainability import ExplainabilityResponse
from app.models.explainability_cache import ExplainabilityCache
from app.models.prediction_history import PredictionHistory
from app.models.ndvi_cache import NDVICache

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
WEATHER_DAILY_PATH = os.path.join(DATA_DIR, "weather_daily.csv")
WEATHER_YEARLY_PATH = os.path.join(DATA_DIR, "weather_yearly.csv")


def _get_weather_data_for_region(region: str) -> tuple[float, float]:
    """
    Read weather dataset and aggregate average daily rainfall and temperature
    for the specified region.
    Returns (avg_rainfall, avg_temperature).
    """
    try:
        if os.path.exists(WEATHER_DAILY_PATH):
            df = pd.read_csv(WEATHER_DAILY_PATH)
            if "region" in df.columns:
                region_df = df[df["region"].astype(str).str.lower() == region.lower()]
                if not region_df.empty:
                    df = region_df

            avg_temp = float(df["temperature"].mean()) if "temperature" in df.columns else 25.0
            avg_rain = float(df["rainfall"].mean()) if "rainfall" in df.columns else 5.0
            return round(avg_rain, 2), round(avg_temp, 2)

        elif os.path.exists(WEATHER_YEARLY_PATH):
            df = pd.read_csv(WEATHER_YEARLY_PATH)
            if "region" in df.columns:
                region_df = df[df["region"].astype(str).str.lower() == region.lower()]
                if not region_df.empty:
                    df = region_df

            avg_temp = float(df["avg_temperature"].mean()) if "avg_temperature" in df.columns else 25.0
            avg_rain = float(df["total_rainfall"].mean() / 365.0) if "total_rainfall" in df.columns else 5.0
            return round(avg_rain, 2), round(avg_temp, 2)
    except Exception:
        pass

    return 5.0, 25.0


def _get_ndvi_data_for_region(region: str, db: Session) -> tuple[float | None, str]:
    """
    Query NDVICache for the latest vegetation status and ndvi_value for the region.
    Returns (ndvi_value, vegetation_status).
    """
    ndvi_entry = (
        db.query(NDVICache)
        .filter(NDVICache.region_name == region)
        .order_by(NDVICache.computed_at.desc())
        .first()
    )

    if ndvi_entry and ndvi_entry.ndvi_value is not None:
        return float(ndvi_entry.ndvi_value), ndvi_entry.vegetation_status

    return None, "Data not yet available"


from app.services.llm_service import generate_llm_text


def _compute_contributions(avg_rainfall: float, avg_temp: float, ndvi_val: float | None) -> dict:
    """
    Normalize real environmental indicators into percentage weights summing to 100%.
    """
    effective_ndvi = ndvi_val if ndvi_val is not None else 0.5
    rainfall_score = max(0.1, min(1.0, avg_rainfall / 10.0))
    soil_score = max(0.1, min(1.0, effective_ndvi))
    temp_score = max(0.1, min(1.0, avg_temp / 35.0))

    total = rainfall_score + soil_score + temp_score

    rainfall_pct = round(rainfall_score / total * 100, 1)
    soil_pct = round(soil_score / total * 100, 1)
    temperature_pct = round(temp_score / total * 100, 1)

    # Correct floating point rounding difference to ensure exact 100% total
    diff = round(100.0 - (rainfall_pct + soil_pct + temperature_pct), 1)
    if diff != 0:
        rainfall_pct = round(rainfall_pct + diff, 1)

    return {
        "rainfall": rainfall_pct,
        "soil": soil_pct,
        "temperature": temperature_pct,
    }


def get_explanation(prediction_id: int, db: Session) -> ExplainabilityResponse | None:
    # ── 1. Check cache first ──────────────────────────────────────────────────
    cached = db.query(ExplainabilityCache).filter(
        ExplainabilityCache.prediction_id == prediction_id,
    ).first()

    if cached:
        return ExplainabilityResponse(
            prediction_id=cached.prediction_id,
            crop=cached.crop,
            region=cached.region,
            contributions=cached.contributions,
            top_factor=cached.top_factor,
            summary_text_bn=cached.summary_text_bn,
        )

    # ── 2. Verify prediction_id exists in PredictionHistory ───────────────────
    prediction = db.query(PredictionHistory).filter(
        PredictionHistory.id == prediction_id
    ).first()

    if not prediction:
        return None

    # ── 3. Fetch real environmental data for prediction's region ──────────────
    avg_rainfall, avg_temp = _get_weather_data_for_region(prediction.region)
    ndvi_val, veg_status = _get_ndvi_data_for_region(prediction.region, db)

    # ── 4. Build rule-based contribution breakdown ────────────────────────────
    contributions = _compute_contributions(avg_rainfall, avg_temp, ndvi_val)
    top_factor = max(contributions, key=contributions.get)

    # ── 5. Generate honest, contextual Gemini LLM Bengali summary text ────────
    ndvi_text = f"{ndvi_val:.2f} ({veg_status})" if ndvi_val is not None else "উপাত্ত প্রক্রিয়াধীন"
    fallback_summary_bn = (
        f"{prediction.region} অঞ্চলের পরিবেশগত প্রেক্ষিত: "
        f"গড় বৃষ্টিপাত {avg_rainfall:.1f} মিমি, গড় তাপমাত্রা {avg_temp:.1f}°সে, "
        f"এবং স্যাটেলাইট NDVI অবস্থা {ndvi_text}। "
        f"ফসলের জাত ({prediction.variety}) ও চাষ পদ্ধতি ({prediction.cropping_type}) "
        f"সহ এই পরিবেশগত মানগুলো পূর্বাভাসে সহায়তা করে।"
    )

    prompt = (
        f"তুমি একজন সেরা কৃষি পরিবেশবিদ। {prediction.region} অঞ্চলে {prediction.crop} ফসলের পরিবেশগত অবস্থা: "
        f"গড় বৃষ্টিপাত {avg_rainfall:.1f}মিমি, গড় তাপমাত্রা {avg_temp:.1f}°সে, "
        f"স্যাটেলাইট NDVI সূচক {ndvi_text}, জাত: {prediction.variety}, চাষ পদ্ধতি: {prediction.cropping_type}। "
        f"কৃষকের বোঝার সুবিধার্থে ২-৩ বাক্যে সহজ ও বাস্তবসম্মত বাংলা পরিবেশগত ব্যাখ্যা লিখে দাও। Markdown বা bullet বাদ দাও।"
    )

    summary_text_bn = generate_llm_text(prompt, fallback_text=fallback_summary_bn)

    # ── 6. Cache only if real satellite data was available ────────────────────
    if ndvi_val is not None:
        try:
            new_entry = ExplainabilityCache(
                prediction_id=prediction_id,
                crop=prediction.crop,
                region=prediction.region,
                contributions=contributions,
                top_factor=top_factor,
                summary_text_bn=summary_text_bn,
            )
            db.add(new_entry)
            db.commit()
        except Exception:
            db.rollback()

    return ExplainabilityResponse(
        prediction_id=prediction_id,
        crop=prediction.crop,
        region=prediction.region,
        contributions=contributions,
        top_factor=top_factor,
        summary_text_bn=summary_text_bn,
    )
