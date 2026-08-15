from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from schemas.risk_schema import WeatherScenario

class AdvisoryRequest(BaseModel):
    variety_id: int
    scenario: WeatherScenario

class AdvisoryResponse(BaseModel):
    id: Optional[int] = None
    variety_id: int
    variety_name: str
    variety_name_bangla: str
    risk_level: str
    advisory_text_bn: str
    action_items_bn: List[str]
    irrigation_advice_bn: str
    pest_advice_bn: str
    llm_provider: str
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
