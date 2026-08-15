from typing import List
from pydantic import BaseModel

class ForecastPoint(BaseModel):
    ds: str
    yhat: float
    yhat_lower: float
    yhat_upper: float

class ForecastResponse(BaseModel):
    variety_id: int
    metric_type: str
    points: List[ForecastPoint]
