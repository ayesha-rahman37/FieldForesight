from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.scenario_planner import ScenarioResponse, ScenarioRequest
from app.services.scenario_planner_service import run_scenario

router = APIRouter()


@router.post("/", response_model=ScenarioResponse)
def scenario(request: ScenarioRequest, db: Session = Depends(get_db)):
    return run_scenario(
        request.crop,
        request.region,
        request.variety,
        request.cropping_type,
        request.rainfall_adjustment_percent,
        request.temperature_adjustment_percent,
        db=db,
    )