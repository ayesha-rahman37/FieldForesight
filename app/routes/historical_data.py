from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.crop import Crop
from app.models.region import Region
from app.models.historical_yield import HistoricalYield
from app.services.regional_fallback import (
    get_regional_historical_data,
)


router = APIRouter()


@router.get("/historical-data")
def get_historical_data(
    crop: str,
    region: str,
    db: Session = Depends(get_db),
):
    crop_obj = (
        db.query(Crop)
        .filter(Crop.name == crop)
        .first()
    )

    region_obj = (
        db.query(Region)
        .filter(Region.name == region)
        .first()
    )

    # ---------------------------------------------------------
    # LOCAL HISTORICAL DATA
    # ---------------------------------------------------------
    # Use local database data only when both crop and region
    # exist and matching historical records are available.

    if crop_obj and region_obj:

        records = (
            db.query(HistoricalYield)
            .filter(
                HistoricalYield.crop_id == crop_obj.id,
                HistoricalYield.region_id == region_obj.id,
            )
            .order_by(
                HistoricalYield.year.asc()
            )
            .all()
        )

        if records:
            return {
                "years": [
                    r.year
                    for r in records
                ],
                "rainfall": [
                    r.rainfall
                    for r in records
                ],
                "yield": [
                    r.yield_value
                    for r in records
                ],
                "source_type": "local_historical",
            }

    # ---------------------------------------------------------
    # FALLBACK HISTORICAL DATA
    # ---------------------------------------------------------
    try:

        return get_regional_historical_data(
            crop=crop,
            region=region,
        )

    except FileNotFoundError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc