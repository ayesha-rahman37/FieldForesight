from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.community import CommunityYieldAggregationResponse
from app.services.get_community_aggregation import get_community_aggregation

router = APIRouter()

@router.get("/", response_model=CommunityYieldAggregationResponse)
def community_endpoint(
    region: str,
    crop: str,
    llm_prediction: float,
    db: Session = Depends(get_db),
):
    return get_community_aggregation(region, crop, llm_prediction, db)