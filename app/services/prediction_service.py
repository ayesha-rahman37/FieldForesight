import os
from datetime import datetime, timedelta, timezone
import joblib
from sqlalchemy.orm import Session

from app.data.district_coordinates import normalize_region_name
from app.models.crop import Crop
from app.models.forecast_cache import ForecastCache
from app.models.historical_yield import HistoricalYield
from app.models.model_metadata import ModelMetadata
from app.models.region import Region
from app.services.adjustment_rules import apply_adjustments
from app.services.regional_fallback import (
    FALLBACK_MODEL_VERSION,
    get_fallback_prediction,
)

# Crop-specific agronomic climate sensitivity coefficients
# (rainfall_linear_per_10pct, temp_linear_per_1degC, heat_stress_penalty_per_degC_above_1)
CROP_CLIMATE_SENSITIVITY = {
    "Rice": (0.032, -0.022, -0.015),
    "Wheat": (0.018, -0.042, -0.025),
    "Maize": (0.024, -0.028, -0.018),
    "Potato": (0.020, -0.038, -0.022),
    "Jute": (0.035, 0.012, -0.014),
    "Mustard": (0.016, -0.034, -0.020),
    "Lentil": (0.015, -0.030, -0.018),
}


def _utcnow_naive():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def get_latest_model_metadata(
    db: Session,
    crop: str,
    region: str,
):
    clean_crop = crop.strip()
    canonical_region = normalize_region_name(region)
    return (
        db.query(ModelMetadata)
        .filter(
            ModelMetadata.crop.ilike(clean_crop),
            (ModelMetadata.region.ilike(canonical_region)) | (ModelMetadata.region.ilike(region.strip())),
        )
        .order_by(ModelMetadata.trained_at.desc())
        .first()
    )


def _get_default_future_rainfall(db: Session, crop: str, region: str) -> float:
    clean_crop = crop.strip()
    canonical_region = normalize_region_name(region)
    records = (
        db.query(HistoricalYield.rainfall)
        .join(Crop, HistoricalYield.crop_id == Crop.id)
        .join(Region, HistoricalYield.region_id == Region.id)
        .filter(
            Crop.name.ilike(clean_crop),
            Region.name.ilike(canonical_region),
            HistoricalYield.rainfall.isnot(None),
        )
        .order_by(HistoricalYield.year.desc())
        .limit(3)
        .all()
    )
    if records:
        vals = [float(r[0]) for r in records if r[0] is not None]
        if vals:
            return sum(vals) / len(vals)
    return 1850.0


def _compute_climate_multiplier(
    crop: str,
    rainfall_adjustment_percent: float,
    temperature_adjustment_percent: float,
    prophet_has_rainfall_regressor: bool = False,
) -> float:
    """
    Computes agronomic yield multiplier for rainfall (% change) and temperature shift
    (where temperature_adjustment_percent = temp_shift_celsius * 10).
    """
    rain_sens, temp_sens, heat_penalty = CROP_CLIMATE_SENSITIVITY.get(
        crop, (0.025, -0.025, -0.018)
    )
    temp_shift_c = temperature_adjustment_percent / 10.0

    # If Prophet already applied its learned linear rainfall regressor, apply only non-linear flood/drought stress
    if prophet_has_rainfall_regressor:
        rain_effect = (rainfall_adjustment_percent / 10.0) * (rain_sens * 0.45)
    else:
        rain_effect = (rainfall_adjustment_percent / 10.0) * rain_sens

    # Extreme drought (< -25%) or waterlogging (> +30%) quadratic penalty
    if rainfall_adjustment_percent < -25.0:
        excess_drought = abs(rainfall_adjustment_percent + 25.0) / 10.0
        rain_effect -= 0.018 * (excess_drought ** 1.35)
    elif rainfall_adjustment_percent > 30.0:
        excess_flood = (rainfall_adjustment_percent - 30.0) / 10.0
        rain_effect -= 0.022 * (excess_flood ** 1.35)

    # Temperature shift effect
    temp_effect = temp_shift_c * temp_sens
    if abs(temp_shift_c) > 1.5:
        temp_effect += (abs(temp_shift_c) - 1.5) * heat_penalty

    return max(0.35, 1.0 + rain_effect + temp_effect)


def get_prediction(
    crop: str,
    region: str,
    variety: str = "HYV",
    cropping_type: str = "single",
    db: Session | None = None,
    rainfall_adjustment_percent: float = 0.0,
    temperature_adjustment_percent: float = 0.0,
):
    if db is None:
        raise ValueError("Database session is required for prediction.")

    clean_crop = crop.strip().title()
    canonical_region = normalize_region_name(region)
    clean_variety = (variety or "HYV").strip()
    clean_cropping = (cropping_type or "single").strip().lower()
    is_simulated = (
        abs(rainfall_adjustment_percent) > 1e-4
        or abs(temperature_adjustment_percent) > 1e-4
    )

    metadata = get_latest_model_metadata(db, clean_crop, canonical_region)

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    disk_filename = f"{clean_crop.lower().replace(' ', '_')}__{canonical_region.lower().replace(' ', '_')}.pkl"
    default_disk_path = os.path.join(repo_root, "app", "data", "models", disk_filename)

    if metadata is None and not os.path.exists(default_disk_path):
        ttl_cutoff = _utcnow_naive() - timedelta(days=1)
        if not is_simulated:
            cached = (
                db.query(ForecastCache)
                .filter(
                    ForecastCache.crop.ilike(clean_crop),
                    ForecastCache.region.ilike(canonical_region),
                    ForecastCache.variety.ilike(clean_variety),
                    ForecastCache.cropping_type.ilike(clean_cropping),
                    ForecastCache.model_version == FALLBACK_MODEL_VERSION,
                    ForecastCache.created_at >= ttl_cutoff,
                )
                .order_by(ForecastCache.created_at.desc())
                .first()
            )

            if cached:
                return {
                    "predicted_yield": cached.predicted_yield,
                    "lower_bound": cached.lower_bound,
                    "upper_bound": cached.upper_bound,
                    "message": f"Cached regionalized forecast returned for {clean_crop} in {canonical_region}.",
                    "model_version": FALLBACK_MODEL_VERSION,
                    "cache_hit": True,
                }

        result = get_fallback_prediction(
            crop=clean_crop,
            region=canonical_region,
            variety=clean_variety,
            cropping_type=clean_cropping,
        )

        if is_simulated:
            mult = _compute_climate_multiplier(
                clean_crop,
                rainfall_adjustment_percent,
                temperature_adjustment_percent,
                prophet_has_rainfall_regressor=False,
            )
            result["predicted_yield"] = round(max(0.1, result["predicted_yield"] * mult), 2)
            result["lower_bound"] = round(max(0.1, result["lower_bound"] * mult), 2)
            result["upper_bound"] = round(max(0.1, result["upper_bound"] * mult), 2)
            return result

        cache_entry = ForecastCache(
            crop=clean_crop,
            region=canonical_region,
            variety=clean_variety,
            cropping_type=clean_cropping,
            model_version=result["model_version"],
            predicted_yield=result["predicted_yield"],
            lower_bound=result["lower_bound"],
            upper_bound=result["upper_bound"],
        )
        db.add(cache_entry)
        db.commit()
        return result

    # ---------------------------------------------------------
    # LOCAL MODEL PATH (with Prophet Regressor & Cloud-Fallback)
    # ---------------------------------------------------------
    active_model_version = metadata.model_version if metadata else "prophet-disk-v1"
    ttl_cutoff = _utcnow_naive() - timedelta(days=1)
    if not is_simulated:
        cached = (
            db.query(ForecastCache)
            .filter(
                ForecastCache.crop.ilike(clean_crop),
                ForecastCache.region.ilike(canonical_region),
                ForecastCache.variety.ilike(clean_variety),
                ForecastCache.cropping_type.ilike(clean_cropping),
                ForecastCache.model_version == active_model_version,
                ForecastCache.created_at >= ttl_cutoff,
            )
            .order_by(ForecastCache.created_at.desc())
            .first()
        )

        if cached:
            return {
                "predicted_yield": cached.predicted_yield,
                "lower_bound": cached.lower_bound,
                "upper_bound": cached.upper_bound,
                "message": f"Cached yield prediction returned for {clean_crop} in {canonical_region}.",
                "model_version": active_model_version,
                "cache_hit": True,
            }

    if metadata:
        model_path = os.path.normpath(os.path.join(repo_root, metadata.model_path.lstrip("/\\")))
    else:
        model_path = default_disk_path

    if not os.path.exists(model_path):
        return get_fallback_prediction(
            crop=clean_crop,
            region=canonical_region,
            variety=clean_variety,
            cropping_type=clean_cropping,
        )

    has_rainfall_reg = False
    try:
        model = joblib.load(model_path)
        future = model.make_future_dataframe(periods=1, freq="YS")
        extra_regressors = getattr(model, "extra_regressors", {}) or {}
        if "rainfall" in extra_regressors:
            has_rainfall_reg = True
            base_rain = _get_default_future_rainfall(db, clean_crop, canonical_region)
            simulated_rain = max(50.0, base_rain * (1.0 + rainfall_adjustment_percent / 100.0))
            future["rainfall"] = simulated_rain

        forecast = model.predict(future)
        latest = forecast.iloc[-1]

        base_yield = float(latest["yhat"])
        lower = float(latest["yhat_lower"])
        upper = float(latest["yhat_upper"])
    except Exception as exc:
        print(f"Failed to load local Prophet model ({exc}), falling back to regional model.")
        return get_fallback_prediction(
            crop=clean_crop,
            region=canonical_region,
            variety=clean_variety,
            cropping_type=clean_cropping,
        )

    if is_simulated:
        mult = _compute_climate_multiplier(
            clean_crop,
            rainfall_adjustment_percent,
            temperature_adjustment_percent,
            prophet_has_rainfall_regressor=has_rainfall_reg,
        )
        base_yield *= mult
        lower *= mult
        upper *= mult

    adjusted_yield = apply_adjustments(base_yield, clean_variety, clean_cropping)
    adjusted_lower = apply_adjustments(lower, clean_variety, clean_cropping)
    adjusted_upper = apply_adjustments(upper, clean_variety, clean_cropping)

    training_records = metadata.training_records if metadata else 10
    if training_records < 8:
        fallback_weight = max(0.0, min(1.0, (8 - training_records) / 8.0))
        try:
            fb = get_fallback_prediction(clean_crop, canonical_region, clean_variety, clean_cropping)
            adjusted_yield = round((1.0 - fallback_weight) * adjusted_yield + fallback_weight * fb["predicted_yield"], 2)
            adjusted_lower = round((1.0 - fallback_weight) * adjusted_lower + fallback_weight * fb["lower_bound"], 2)
            adjusted_upper = round((1.0 - fallback_weight) * adjusted_upper + fallback_weight * fb["upper_bound"], 2)
        except Exception:
            pass

    if not is_simulated:
        cache_entry = ForecastCache(
            crop=clean_crop,
            region=canonical_region,
            variety=clean_variety,
            cropping_type=clean_cropping,
            model_version=active_model_version,
            predicted_yield=adjusted_yield,
            lower_bound=adjusted_lower,
            upper_bound=adjusted_upper,
        )
        db.add(cache_entry)
        db.commit()

    return {
        "predicted_yield": adjusted_yield,
        "lower_bound": adjusted_lower,
        "upper_bound": adjusted_upper,
        "message": (
            f"Yield prediction generated for {clean_crop} in {canonical_region} "
            f"using {clean_variety} variety and {clean_cropping} cropping."
        ),
        "model_version": active_model_version,
        "cache_hit": False,
    }
