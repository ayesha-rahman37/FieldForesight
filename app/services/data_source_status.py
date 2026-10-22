import os
from pathlib import Path
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.ndvi_cache import NDVICache
from app.models.soil_cache import SoilCache

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")

NASA_POWER_URL = (
    "https://power.larc.nasa.gov/api/temporal/daily/point"
)


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
            timeout=8,
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

    soil_count = (
        db.query(func.count(SoilCache.id))
        .filter(SoilCache.status == "available")
        .scalar()
        or 0
    )

    latest_soil = (
        db.query(func.max(SoilCache.fetched_at))
        .filter(SoilCache.status == "available")
        .scalar()
    )

    satellite_configured = bool(
        os.getenv("SENTINELHUB_CLIENT_ID")
        and os.getenv("SENTINELHUB_CLIENT_SECRET")
    )

    return {
        "weather": check_weather_api(),
        "soil": {
            "status": (
                "cached_data_available"
                if soil_count
                else "configured_no_cached_data"
            ),
            "provider": "SoilGrids",
            "regions_with_soil_data": soil_count,
            "latest_fetched_at": (
                latest_soil.isoformat() if latest_soil else None
            ),
            "live_connection_checked": False,
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
            "provider": "Sentinel Hub",
            "credentials_configured": satellite_configured,
            "regions_with_ndvi": ndvi_count,
            "latest_computed_at": (
                latest_ndvi.isoformat() if latest_ndvi else None
            ),
            "live_connection_checked": False,
        },
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }