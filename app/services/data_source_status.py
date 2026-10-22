import os
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.model_metadata import ModelMetadata
from app.models.ndvi_cache import NDVICache

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")

NASA_POWER_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"


def check_weather_api() -> dict:
    """Check NASA POWER connectivity using a small historical request."""
    params = {
        "parameters": "T2M",
        "community": "AG",
        "longitude": 90.4125,
        "latitude": 23.8103,
        "start": "20240101",
        "end": "20240102",
        "format": "JSON",
    }

    try:
        response = requests.get(
            NASA_POWER_URL,
            params=params,
            timeout=5,
        )
        response.raise_for_status()
        data = response.json()
        temperatures = (
            data.get("properties", {})
            .get("parameter", {})
            .get("T2M", {})
        )

        if not temperatures:
            return {
                "status": "unavailable",
                "provider": "NASA POWER",
                "live_connection_checked": True,
                "message": "The API returned no temperature data.",
            }

        return {
            "status": "available",
            "provider": "NASA POWER",
            "api_key_required": False,
            "live_connection_checked": True,
        }

    except Exception as exc:
        return {
            "status": "unavailable",
            "provider": "NASA POWER",
            "api_key_required": False,
            "live_connection_checked": True,
            "message": f"Weather check failed: {type(exc).__name__}",
        }


def get_data_source_status(db: Session) -> dict:
    ndvi_count = (
        db.query(func.count(NDVICache.id))
        .filter(NDVICache.ndvi_value.isnot(None))
        .scalar()
        or 0
    )

    latest_ndvi = (
        db.query(func.max(NDVICache.computed_at))
        .filter(NDVICache.ndvi_value.isnot(None))
        .scalar()
    )

    model_count = db.query(func.count(ModelMetadata.id)).scalar() or 0

    satellite_configured = bool(
        os.getenv("SENTINELHUB_CLIENT_ID")
        and os.getenv("SENTINELHUB_CLIENT_SECRET")
    )

    return {
        "weather": check_weather_api(),
        "soil": {
            "status": "available" if ndvi_count > 0 else "unavailable",
            "provider": "DAE / BARC Regional Calibration",
            "message": "Regional soil & agro-ecological calibration active.",
        },
        "satellite": {
            "status": (
                "cached_data_available"
                if ndvi_count
                else (
                    "configured_no_cached_data"
                    if satellite_configured
                    else "not_configured"
                )
            ),
            "provider": "Sentinel Hub (Sentinel-2 L2A)",
            "credentials_configured": satellite_configured,
            "regions_with_ndvi": ndvi_count,
            "latest_computed_at": latest_ndvi.isoformat() if latest_ndvi else None,
            "live_connection_checked": False,
        },
        "models": {
            "trained_models_count": model_count,
            "fallback_enabled": True,
        },
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }

