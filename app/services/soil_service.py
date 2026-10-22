
from datetime import datetime, timedelta, timezone

import requests
from sqlalchemy.orm import Session

from app.data.district_coordinates import DISTRICT_COORDINATES
from app.models.soil_cache import SoilCache

SOILGRIDS_URL = (
    "https://rest.isric.org/soilgrids/v2.0/properties/query"
)
CACHE_MAX_AGE = timedelta(days=30)

PROPERTIES = {
    "ph": "phh2o",
    "organic_carbon": "soc",
    "clay_content": "clay",
    "sand_content": "sand",
    "nitrogen": "nitrogen",
}


def fetch_soil_from_provider(latitude: float, longitude: float) -> dict:
    """Fetch topsoil properties from SoilGrids.

    SoilGrids may be unavailable. Never invent soil values.
    """
    response = requests.get(
        SOILGRIDS_URL,
        params=[
            ("lon", longitude),
            ("lat", latitude),
            *[("property", prop) for prop in PROPERTIES.values()],
            ("depth", "0-5cm"),
            ("value", "mean"),
        ],
        timeout=12,
    )
    response.raise_for_status()
    payload = response.json()

    layers = payload.get("properties", {}).get("layers", [])
    result = {}

    for layer in layers:
        name = layer.get("name")
        field = next(
            (
                key
                for key, provider_name in PROPERTIES.items()
                if provider_name == name
            ),
            None,
        )
        if not field:
            continue

        depths = layer.get("depths", [])
        if not depths:
            continue

        values = depths[0].get("values", {})
        value = values.get("mean")

        if isinstance(value, (int, float)):
            result[field] = float(value)

    if not result:
        raise ValueError("Soil provider returned no usable property values")

    return result


def get_soil_data(region: str, db: Session) -> dict:
    """Return cached soil properties or try the live provider."""
    coordinates = DISTRICT_COORDINATES.get(region)
    if not coordinates:
        return {
            "status": "unavailable",
            "provider": "SoilGrids",
            "message": "Unknown district",
        }

    latitude, longitude = coordinates
    cached = (
        db.query(SoilCache)
        .filter(SoilCache.region_name == region)
        .first()
    )

    now = datetime.now(timezone.utc)

    if cached and cached.status == "available" and cached.fetched_at:
        fetched_at = cached.fetched_at
        if fetched_at.tzinfo is None:
            fetched_at = fetched_at.replace(tzinfo=timezone.utc)

        if now - fetched_at < CACHE_MAX_AGE:
            return _serialize(cached, "cached")

    try:
        values = fetch_soil_from_provider(latitude, longitude)

        if cached is None:
            cached = SoilCache(
                region_name=region,
                latitude=latitude,
                longitude=longitude,
            )
            db.add(cached)

        for field, value in values.items():
            setattr(cached, field, value)

        cached.provider = "SoilGrids"
        cached.status = "available"
        cached.fetched_at = datetime.now(timezone.utc).replace(tzinfo=None)
        cached.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        db.commit()
        db.refresh(cached)

        return _serialize(cached, "live")

    except (requests.RequestException, ValueError) as exc:
        db.rollback()

        if cached and cached.status == "available":
            return _serialize(cached, "stale_cache")

        return {
            "status": "unavailable",
            "provider": "SoilGrids",
            "message": f"Soil data could not be retrieved ({type(exc).__name__})",
        }


def _serialize(record: SoilCache, source_status: str) -> dict:
    return {
        "status": "available",
        "provider": record.provider,
        "data_status": source_status,
        "latitude": record.latitude,
        "longitude": record.longitude,
        "depth": "0-5cm",
        "ph": record.ph,
        "organic_carbon": record.organic_carbon,
        "clay_content": record.clay_content,
        "sand_content": record.sand_content,
        "nitrogen": record.nitrogen,
        "fetched_at": (
            record.fetched_at.isoformat() if record.fetched_at else None
        ),
    }
