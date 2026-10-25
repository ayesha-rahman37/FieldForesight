from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.data.district_coordinates import normalize_region_name
from app.database import get_db
from app.schemas.community import CommunityYieldAggregationResponse
from app.services.get_community_aggregation import get_community_aggregation

router = APIRouter()


@router.get("/", response_model=CommunityYieldAggregationResponse)
@router.get("", response_model=CommunityYieldAggregationResponse, include_in_schema=False)
def community_endpoint(
    region: str = "Rangpur",
    crop: str = "Rice",
    llm_prediction: float = 4.2,
    db: Session = Depends(get_db),
):
    canonical_region = normalize_region_name(region)
    return get_community_aggregation(canonical_region, crop, llm_prediction, db)
