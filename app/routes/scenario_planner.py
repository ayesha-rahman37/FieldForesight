from fastapi import APIRouter

from app.schemas.scenario_planner import ScenarioResponse, ScenarioRequest
from app.services.scenario_planner_service import run_scenario

router = APIRouter()


@router.post("/",response_model=ScenarioResponse)
def scenario(request: ScenarioRequest):
    return run_scenario(request.crop, request.region, request.variety,
        request.cropping_type, request.rainfall_adjustment_percent)