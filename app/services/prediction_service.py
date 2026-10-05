import os
from datetime import datetime, timedelta
import joblib
from sqlalchemy.orm import Session

from app.models.forecast_cache import ForecastCache
from app.models.model_metadata import ModelMetadata
from app.services.adjustment_rules import apply_adjustments
from app.services.regional_fallback import (
    FALLBACK_MODEL_VERSION,
    get_fallback_prediction,
)


def get_latest_model_metadata(
    db: Session,
    crop: str,
    region: str,
):
    return (
        db.query(ModelMetadata)
        .filter(
            ModelMetadata.crop == crop,
            ModelMetadata.region == region,
        )
        .order_by(
            ModelMetadata.trained_at.desc()
        )
        .first()
    )


def get_prediction(
    crop: str,
    region: str,
    variety: str = "HYV",
    cropping_type: str = "single",
    db: Session | None = None,
):
    if db is None:
        raise ValueError(
            "Database session is required for prediction."
        )

    metadata = get_latest_model_metadata(
        db,
        crop,
        region,
    )

    # ---------------------------------------------------------
    # FALLBACK PATH
    # ---------------------------------------------------------
    # If a local crop-region Prophet model does not exist,
    # use the documented regionalized fallback model.
    if metadata is None:

        ttl_cutoff = datetime.utcnow() - timedelta(days=1)
        cached = (
            db.query(ForecastCache)
            .filter(
                ForecastCache.crop == crop,
                ForecastCache.region == region,
                ForecastCache.variety == variety,
                ForecastCache.cropping_type == cropping_type,
                ForecastCache.model_version == FALLBACK_MODEL_VERSION,
                ForecastCache.created_at >= ttl_cutoff,
            )
            .order_by(
                ForecastCache.created_at.desc()
            )
            .first()
        )

        if cached:

            return {
                "predicted_yield": cached.predicted_yield,
                "lower_bound": cached.lower_bound,
                "upper_bound": cached.upper_bound,
                "message": (
                    f"Cached regionalized forecast returned "
                    f"for {crop} in {region}."
                ),
                "model_version": FALLBACK_MODEL_VERSION,
                "cache_hit": True,
            }

        result = get_fallback_prediction(
            crop=crop,
            region=region,
            variety=variety,
            cropping_type=cropping_type,
        )

        cache_entry = ForecastCache(
            crop=crop,
            region=region,
            variety=variety,
            cropping_type=cropping_type,
            model_version=result["model_version"],
            predicted_yield=result["predicted_yield"],
            lower_bound=result["lower_bound"],
            upper_bound=result["upper_bound"],
        )

        db.add(cache_entry)
        db.commit()

        return result

    # ---------------------------------------------------------
    # LOCAL MODEL PATH
    # ---------------------------------------------------------

    ttl_cutoff = datetime.utcnow() - timedelta(days=1)
    cached = (
        db.query(ForecastCache)
        .filter(
            ForecastCache.crop == crop,
            ForecastCache.region == region,
            ForecastCache.variety == variety,
            ForecastCache.cropping_type == cropping_type,
            ForecastCache.model_version == metadata.model_version,
            ForecastCache.created_at >= ttl_cutoff,
        )
        .order_by(
            ForecastCache.created_at.desc()
        )
        .first()
    )

    if cached:

        return {
            "predicted_yield": cached.predicted_yield,
            "lower_bound": cached.lower_bound,
            "upper_bound": cached.upper_bound,
            "message": (
                f"Cached yield prediction returned "
                f"for {crop} in {region}."
            ),
            "model_version": metadata.model_version,
            "cache_hit": True,
        }

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    model_path = os.path.normpath(
        os.path.join(repo_root, metadata.model_path.lstrip("/\\"))
    )

    if not os.path.exists(model_path):
        return get_fallback_prediction(
            crop=crop,
            region=region,
            variety=variety,
            cropping_type=cropping_type,
        )

    try:
        model = joblib.load(
            model_path
        )

        future = model.make_future_dataframe(
            periods=1,
            freq="YS",
        )

        forecast = model.predict(
            future
        )

        latest = forecast.iloc[-1]

        base_yield = float(
            latest["yhat"]
        )

        lower = float(
            latest["yhat_lower"]
        )
    except Exception as exc:
        print(f"Failed to load local Prophet model ({exc}), falling back to regional model.")
        return get_fallback_prediction(
            crop=crop,
            region=region,
            variety=variety,
            cropping_type=cropping_type,
        )

    upper = float(
        latest["yhat_upper"]
    )


    adjusted_yield = apply_adjustments(
        base_yield,
        variety,
        cropping_type,
    )

    adjusted_lower = apply_adjustments(
        lower,
        variety,
        cropping_type,
    )

    adjusted_upper = apply_adjustments(
        upper,
        variety,
        cropping_type,
    )

    cache_entry = ForecastCache(
        crop=crop,
        region=region,
        variety=variety,
        cropping_type=cropping_type,
        model_version=metadata.model_version,
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
            f"Yield prediction generated for {crop} "
            f"in {region} using {variety} variety "
            f"and {cropping_type} cropping."
        ),
        "model_version": metadata.model_version,
        "cache_hit": False,
    }