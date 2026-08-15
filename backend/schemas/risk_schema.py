from typing import List, Optional, Dict
from pydantic import BaseModel, ConfigDict, Field

class RiskThresholdBase(BaseModel):
    variety_id: int
    metric_name: str
    low_max: float
    medium_max: float
    high_max: float
    critical_min: float
    advisory_note_bn: Optional[str] = None

class RiskThresholdCreate(RiskThresholdBase):
    pass

class RiskThresholdResponse(RiskThresholdBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class WeatherScenario(BaseModel):
    temperature: float = Field(default=28.0, description="Temperature in °C")
    humidity: float = Field(default=75.0, ge=0.0, le=100.0, description="Relative humidity percentage")
    rainfall: float = Field(default=150.0, ge=0.0, description="Rainfall in mm")
    wind_speed: float = Field(default=12.0, ge=0.0, description="Wind speed in km/h")
    pest_density: float = Field(default=15.0, ge=0.0, description="Pest density per m²")

class RiskEvaluationResult(BaseModel):
    variety_id: int
    variety_name: str
    variety_name_bangla: str
    risk_level: str
    overall_risk_score: float
    metric_scores: Dict[str, float]
    metric_levels: Dict[str, str]
    triggered_warnings: List[str]
    scenario: WeatherScenario
