import os
import joblib
from pathlib import Path
from sqlalchemy.orm import Session

from app.models.forecast_cache import ForecastCache
from app.models.model_metadata import ModelMetadata
from app.services.adjustment_rules import apply_adjustments
from app.services.regional_fallback import (
    FALLBACK_MODEL_VERSION,
    get_fallback_prediction,
)

MODEL_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "trained_model.pkl"
)


def get_prediction(
    crop: str,
    region: str,
    variety: str = "HYV",
    cropping_type: str = "single",
    db: Session | None = None,
):
    if db is None:
        raise ValueError("Database session is required for prediction.")

    metadata = (
        db.query(ModelMetadata)
        .filter(
            ModelMetadata.crop == crop,
            ModelMetadata.region == region,
        )
        .order_by(ModelMetadata.trained_at.desc())
        .first()
    )

    model_version = (
        metadata.model_version if metadata else FALLBACK_MODEL_VERSION
    )

    cached = (
        db.query(ForecastCache)
        .filter(
            ForecastCache.crop == crop,
            ForecastCache.region == region,
            ForecastCache.variety == variety,
            ForecastCache.cropping_type == cropping_type,
            ForecastCache.model_version == model_version,
        )
        .order_by(ForecastCache.created_at.desc())
        .first()
    )

    if cached:
        return {
            "predicted_yield": cached.predicted_yield,
            "lower_bound": cached.lower_bound,
            "upper_bound": cached.upper_bound,
            "message": f"Cached yield prediction returned for {crop} in {region}.",
            "model_version": model_version,
            "cache_hit": True,
        }

    if metadata is None:
        result = get_fallback_prediction(
            crop=crop,
            region=region,
            variety=variety,
            cropping_type=cropping_type,
        )
        db.add(ForecastCache(
            crop=crop,
            region=region,
            variety=variety,
            cropping_type=cropping_type,
            model_version=result["model_version"],
            predicted_yield=result["predicted_yield"],
            lower_bound=result["lower_bound"],
            upper_bound=result["upper_bound"],
        ))
        db.commit()
        return result

    model_path = Path(metadata.model_path)
    if not model_path.is_absolute():
        model_path = Path(__file__).resolve().parents[2] / model_path

    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")

    model = joblib.load(model_path)
    future = model.make_future_dataframe(periods=1, freq="YS")
    latest = model.predict(future).iloc[-1]

    predicted = apply_adjustments(
        float(latest["yhat"]), variety, cropping_type
    )
    lower = apply_adjustments(
        float(latest["yhat_lower"]), variety, cropping_type
    )
    upper = apply_adjustments(
        float(latest["yhat_upper"]), variety, cropping_type
    )

    db.add(ForecastCache(
        crop=crop,
        region=region,
        variety=variety,
        cropping_type=cropping_type,
        model_version=metadata.model_version,
        predicted_yield=predicted,
        lower_bound=lower,
        upper_bound=upper,
    ))
    db.commit()

    return {
        "predicted_yield": round(predicted, 2),
        "lower_bound": round(lower, 2),
        "upper_bound": round(upper, 2),
        "message": (
            f"Yield prediction generated for {crop} in {region} "
            f"using {variety} variety and {cropping_type} cropping."
        ),
        "model_version": metadata.model_version,
        "cache_hit": False,
    }