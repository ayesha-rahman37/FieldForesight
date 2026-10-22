
from datetime import datetime

from sqlalchemy.orm import Session

from app.data.district_coordinates import DISTRICT_COORDINATES
from app.data.fetch_weather_data import (
    fetch_weather_data,
    aggregate_to_yearly,
)
from app.services.helper import (
    fetch_ndvi_for_region,
    classify_vegetation,
)
from app.services.soil_service import get_soil_data


def get_regional_environmental_data(
    region: str,
    start_year: int = 2020,
    end_year: int | None = None,
    db: Session | None = None,
) -> dict:
    """Collect weather, satellite, and soil data for a Bangladesh district."""

    if end_year is None:
        end_year = datetime.now().year - 1

    if region not in DISTRICT_COORDINATES:
        return {
            "region": region,
            "weather": {
                "status": "unavailable",
                "error": "Unknown district",
            },
            "satellite": {
                "status": "unavailable",
                "error": "Unknown district",
            },
            "soil": {
                "status": "unavailable",
                "message": "Unknown district",
            },
        }

    latitude, longitude = DISTRICT_COORDINATES[region]

    result = {
        "region": region,
        "weather": {"status": "unavailable"},
        "satellite": {"status": "unavailable"},
        "soil": {"status": "unavailable"},
    }

    # Weather data
    try:
        daily = fetch_weather_data(
            latitude, longitude, start_year, end_year
        )
        yearly = aggregate_to_yearly(daily)

        result["weather"] = {
            "status": "available",
            "source": "NASA POWER",
            "start_year": start_year,
            "end_year": end_year,
            "yearly_data": yearly.to_dict(orient="records"),
        }
    except Exception as exc:
        result["weather"]["error"] = str(exc)

    # Satellite data
    try:
        ndvi = fetch_ndvi_for_region(region)
        result["satellite"] = {
            "status": "available",
            "source": "Sentinel-2 L2A",
            "ndvi_value": ndvi,
            "vegetation_status": classify_vegetation(ndvi),
        }
    except Exception as exc:
        result["satellite"]["error"] = str(exc)

    # Soil data
    if db is not None:
        result["soil"] = get_soil_data(region, db)
    else:
        result["soil"] = {
            "status": "unavailable",
            "provider": "SoilGrids",
            "message": (
                "Database session not supplied; "
                "soil cache unavailable."
            ),
        }

    return result