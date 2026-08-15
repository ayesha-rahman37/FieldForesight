from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Variety
from schemas import ForecastResponse
from services.forecaster import run_prophet_or_fallback_forecast

router = APIRouter(prefix="/api/forecast", tags=["Forecaster"])


@router.get("", response_model=ForecastResponse)
def get_forecast(
    variety_id: int,
    metric_type: str = "yield_index",
    days: int = Query(default=30, ge=1, le=365, description="Number of days to forecast (1 to 365)"),
    db: Session = Depends(get_db)
):
    v = db.query(Variety).filter(Variety.id == variety_id).first()
    if not v:
        raise HTTPException(status_code=404, detail=f"Variety with ID {variety_id} not found")

    return run_prophet_or_fallback_forecast(v, metric_type=metric_type, days=days)
