from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Variety, RiskThreshold
from schemas import RiskThresholdResponse, AdvisoryRequest, RiskEvaluationResult
from services.risk_engine import evaluate_risk

router = APIRouter(prefix="/api", tags=["Risk & Thresholds"])


@router.get("/thresholds", response_model=List[RiskThresholdResponse])
def list_thresholds(variety_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(RiskThreshold)
    if variety_id is not None:
        query = query.filter(RiskThreshold.variety_id == variety_id)
    return query.all()


@router.post("/risk/evaluate", response_model=RiskEvaluationResult)
def evaluate_risk_endpoint(request: AdvisoryRequest, db: Session = Depends(get_db)):
    v = db.query(Variety).filter(Variety.id == request.variety_id).first()
    if not v:
        raise HTTPException(status_code=404, detail=f"Variety with ID {request.variety_id} not found")
    return evaluate_risk(v, request.scenario)
