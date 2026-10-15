from typing import List

from pydantic import BaseModel


class RegionYieldPoint(BaseModel):
    year: int
    yield_value: float

class CommunityYieldAggregationResponse(BaseModel):
    region: str
    crop: str
    district_avg_value: float
    historical_trend: List[RegionYieldPoint]
    llm_prediction: float
    comparison_note_bn: str


