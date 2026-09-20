from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.crop import Crop
from app.models.region import Region
from app.models.historical_yield import HistoricalYield

router = APIRouter()


@router.get("/historical-data")
def get_historical_data(
    crop: str,
    region: str,
    db: Session = Depends(get_db)
):
    crop_obj = db.query(Crop).filter(Crop.name == crop).first()
    region_obj = db.query(Region).filter(Region.name == region).first()

    if not crop_obj or not region_obj:
        raise HTTPException(status_code=404, detail="Crop অথবা Region পাওয়া যায়নি।")

    records = (
        db.query(HistoricalYield)
        .filter(
            HistoricalYield.crop_id == crop_obj.id,
            HistoricalYield.region_id == region_obj.id
        )
        .order_by(HistoricalYield.year.asc())
        .all()
    )

    return {
        "years": [r.year for r in records],
        "rainfall": [r.rainfall for r in records],
        "yield": [r.yield_value for r in records]
    }