from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.explainability import ExplainabilityResponse
from app.services.explainability_service import get_explanation

router = APIRouter()

@router.get("/prediction_id",response_model=ExplainabilityResponse)
def get_explainability(prediction_id: int,db: Session = Depends(get_db)):
           explanation =  get_explanation(prediction_id,db)
           if not explanation:
               raise HTTPException(status_code=404, detail="Prediction id not found")
           return explanation

