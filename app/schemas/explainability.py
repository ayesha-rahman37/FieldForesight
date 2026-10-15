from typing import Dict
from pydantic import BaseModel
class ExplainabilityResponse(BaseModel):
    prediction_id: int
    crop: str
    region: str
    contributions: Dict[str, float]   #{"rainfall": 45.0, "soil": 30.0, "temperature": 25.0}
    top_factor: str
    summary_text_bn: str