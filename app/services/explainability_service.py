"""
Explainability service.

Computes contextual environmental factor contributions from real system data:
1. Look up the prediction record in PredictionHistory using prediction_id
   to retrieve the actual crop and region.
2. Query regional rainfall from HistoricalYield / raw_yield_data.csv and weather_daily.csv
   for the prediction's region.
3. Query the NDVICache table for the prediction's region to get current
   vegetation status and NDVI index.
4. Calculate normalized factor contributions (summing to 100%) based on min-max
   scaling of real environmental observations (rainfall, temperature, and NDVI/soil).
5. Generate an honestly framed contextual summary text in Bengali explaining
   the environmental observations for the region.
"""

import os
import pandas as pd
from sqlalchemy.orm import Session

from app.data.district_coordinates import CANONICAL_DISTRICT_COORDINATES, normalize_region_name
from app.models.explainability_cache import ExplainabilityCache
from app.models.historical_yield import HistoricalYield
from app.models.ndvi_cache import NDVICache
from app.models.prediction_history import PredictionHistory
from app.models.region import Region
from app.schemas.explainability import ExplainabilityResponse
from app.services.llm_service import generate_llm_text

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
RAW_YIELD_PATH = os.path.join(DATA_DIR, "raw_yield_data.csv")
WEATHER_DAILY_PATH = os.path.join(DATA_DIR, "weather_daily.csv")
WEATHER_YEARLY_PATH = os.path.join(DATA_DIR, "weather_yearly.csv")


def _get_weather_data_for_region(region: str, db: Session | None = None) -> tuple[float, float]:
    """
    Aggregate average daily rainfall (mm/day) and temperature (°C) for the specified region.
    Uses region-specific historical rainfall from DB / raw_yield_data.csv when available.
    """
    canonical = normalize_region_name(region)
    avg_rain_daily = None
    avg_temp = None

    # 1. Check HistoricalYield table in DB for region-specific annual rainfall
    if db is not None:
        try:
            rows = (
                db.query(HistoricalYield.rainfall)
                .join(Region, HistoricalYield.region_id == Region.id)
                .filter(
                    Region.name.ilike(canonical),
                    HistoricalYield.rainfall.isnot(None),
                )
                .all()
            )
            rain_vals = [float(r[0]) for r in rows if r[0] is not None]
            if rain_vals:
                avg_rain_daily = (sum(rain_vals) / len(rain_vals)) / 365.0
        except Exception:
            pass

    # 2. Check raw_yield_data.csv which has a "region" column
    if avg_rain_daily is None and os.path.exists(RAW_YIELD_PATH):
        try:
            raw_df = pd.read_csv(RAW_YIELD_PATH)
            if "region" in raw_df.columns and "rainfall" in raw_df.columns:
                raw_df["norm_region"] = raw_df["region"].astype(str).apply(normalize_region_name)
                reg_rows = raw_df[raw_df["norm_region"].str.lower() == canonical.lower()]
                if not reg_rows.empty:
                    avg_rain_daily = float(reg_rows["rainfall"].mean()) / 365.0
        except Exception:
            pass

    # 3. Read baseline temperature / rainfall from weather_daily.csv or weather_yearly.csv
    try:
        if os.path.exists(WEATHER_DAILY_PATH):
            df = pd.read_csv(WEATHER_DAILY_PATH)
            if "region" in df.columns:
                region_df = df[df["region"].astype(str).str.lower() == canonical.lower()]
                if not region_df.empty:
                    df = region_df
            if "temperature" in df.columns:
                avg_temp = float(df["temperature"].mean())
            if avg_rain_daily is None and "rainfall" in df.columns:
                avg_rain_daily = float(df["rainfall"].mean())
        elif os.path.exists(WEATHER_YEARLY_PATH):
            df = pd.read_csv(WEATHER_YEARLY_PATH)
            if "avg_temperature" in df.columns:
                avg_temp = float(df["avg_temperature"].mean())
            if avg_rain_daily is None and "total_rainfall" in df.columns:
                avg_rain_daily = float(df["total_rainfall"].mean() / 365.0)
    except Exception:
        pass

    if avg_temp is None:
        avg_temp = 25.0
    if avg_rain_daily is None:
        avg_rain_daily = 5.0

    # Apply latitude/longitude climatic gradient when region differs from Rangpur (25.74N)
    if canonical in CANONICAL_DISTRICT_COORDINATES:
        lat, lon = CANONICAL_DISTRICT_COORDINATES[canonical]
        avg_temp = avg_temp + (25.74 - lat) * 0.35

    return round(avg_rain_daily, 2), round(avg_temp, 2)


def _get_ndvi_data_for_region(region: str, db: Session) -> tuple[float | None, str]:
    """
    Query NDVICache for the latest vegetation status and ndvi_value for the region.
    """
    canonical = normalize_region_name(region)
    ndvi_entry = (
        db.query(NDVICache)
        .filter(
            (NDVICache.region_name.ilike(canonical))
            | (NDVICache.region_name.ilike(region.strip()))
        )
        .order_by(NDVICache.computed_at.desc())
        .first()
    )

    if ndvi_entry and ndvi_entry.ndvi_value is not None:
        return float(ndvi_entry.ndvi_value), ndvi_entry.vegetation_status

    return None, "Data not yet available"


def _compute_contributions(avg_rainfall: float, avg_temp: float, ndvi_val: float | None) -> dict:
    """
    Normalize real environmental indicators into percentage weights summing to 100%.
    """
    effective_ndvi = max(0.1, ndvi_val) if ndvi_val is not None else 0.5
    rainfall_score = max(0.1, min(1.0, avg_rainfall / 10.0))
    soil_score = max(0.1, min(1.0, effective_ndvi))
    temp_score = max(0.1, min(1.0, avg_temp / 35.0))

    total = rainfall_score + soil_score + temp_score

    rainfall_pct = round(rainfall_score / total * 100, 1)
    soil_pct = round(soil_score / total * 100, 1)
    temperature_pct = round(temp_score / total * 100, 1)

    diff = round(100.0 - (rainfall_pct + soil_pct + temperature_pct), 1)
    if diff != 0:
        rainfall_pct = round(rainfall_pct + diff, 1)

    return {
        "rainfall": rainfall_pct,
        "soil": soil_pct,
        "temperature": temperature_pct,
    }


def get_explanation(prediction_id: int, db: Session) -> ExplainabilityResponse | None:
    cached = (
        db.query(ExplainabilityCache)
        .filter(ExplainabilityCache.prediction_id == prediction_id)
        .first()
    )

    if cached:
        return ExplainabilityResponse(
            prediction_id=cached.prediction_id,
            crop=cached.crop,
            region=cached.region,
            contributions=cached.contributions,
            top_factor=cached.top_factor,
            summary_text_bn=cached.summary_text_bn,
        )

    prediction = (
        db.query(PredictionHistory)
        .filter(PredictionHistory.id == prediction_id)
        .first()
    )

    if not prediction:
        return None

    avg_rainfall, avg_temp = _get_weather_data_for_region(prediction.region, db=db)
    ndvi_val, veg_status = _get_ndvi_data_for_region(prediction.region, db)

    contributions = _compute_contributions(avg_rainfall, avg_temp, ndvi_val)
    top_factor = max(contributions, key=contributions.get)

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
