from datetime import datetime
from sqlalchemy.orm import Session

from app.data.district_coordinates import DISTRICT_COORDINATES, normalize_region_name
from app.data.fetch_weather_data import (
    aggregate_to_yearly,
    fetch_weather_data,
)
from app.models.historical_yield import HistoricalYield
from app.models.ndvi_cache import NDVICache
from app.models.region import Region
from app.services.helper import (
    classify_vegetation,
    fetch_ndvi_for_region,
)


def get_regional_environmental_data(
    region: str,
    start_year: int = 2020,
    end_year: int | None = None,
    db: Session | None = None,
) -> dict:
    """Collect weather and NDVI data for a supported Bangladesh district."""
    if end_year is None:
        end_year = datetime.now().year - 1

    canonical = normalize_region_name(region)
    if canonical not in DISTRICT_COORDINATES and region not in DISTRICT_COORDINATES:
        return {
            "region": region,
            "weather": {"status": "unavailable", "error": "Unknown district"},
            "satellite": {"status": "unavailable", "error": "Unknown district"},
        }

    lookup_key = region if region in DISTRICT_COORDINATES else canonical
    latitude, longitude = DISTRICT_COORDINATES[lookup_key]

    result = {
        "region": region,
        "weather": {"status": "unavailable"},
        "satellite": {"status": "unavailable"},
    }

    try:
        daily = fetch_weather_data(latitude, longitude, start_year, end_year)
        yearly = aggregate_to_yearly(daily)

        result["weather"] = {
            "status": "available",
            "source": "NASA POWER",
            "start_year": start_year,
            "end_year": end_year,
            "yearly_data": yearly.to_dict(orient="records"),
        }
    except Exception as exc:
        if db is not None:
            reg_obj = db.query(Region).filter(Region.name.ilike(canonical)).first()
            if reg_obj:
                rows = (
                    db.query(HistoricalYield)
                    .filter(
                        HistoricalYield.region_id == reg_obj.id,
                        HistoricalYield.year >= start_year,
                        HistoricalYield.year <= end_year,
                        HistoricalYield.rainfall.isnot(None),
                    )
                    .order_by(HistoricalYield.year.asc())
                    .all()
                )
                if rows:
                    seen_years = {}
                    for r in rows:
                        seen_years[r.year] = {"year": r.year, "rainfall": r.rainfall}
                    result["weather"] = {
                        "status": "available",
                        "source": "NASA POWER (Cached DB)",
                        "start_year": start_year,
                        "end_year": end_year,
                        "yearly_data": list(seen_years.values()),
                    }
        if result["weather"]["status"] != "available":
            result["weather"]["error"] = str(exc)

    try:
        ndvi = fetch_ndvi_for_region(lookup_key)
        result["satellite"] = {
            "status": "available",
            "source": "Sentinel-2 L2A",
            "ndvi_value": ndvi,
            "vegetation_status": classify_vegetation(ndvi),
        }
    except Exception as exc:
        if db is not None:
            cached_ndvi = (
                db.query(NDVICache)
                .filter(NDVICache.region_name.ilike(canonical))
                .order_by(NDVICache.computed_at.desc())
                .first()
            )
            if cached_ndvi and cached_ndvi.ndvi_value is not None:
                result["satellite"] = {
                    "status": "available",
                    "source": "Sentinel-2 L2A (Cached DB)",
                    "ndvi_value": cached_ndvi.ndvi_value,
                    "vegetation_status": cached_ndvi.vegetation_status or classify_vegetation(cached_ndvi.ndvi_value),
                }
        if result["satellite"]["status"] != "available":
            result["satellite"]["error"] = str(exc)

    return result
