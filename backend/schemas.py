from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class VarietyBase(BaseModel):
    name: str
    name_bangla: str
    crop_type: str
    optimal_temp_min: float = 20.0
    optimal_temp_max: float = 32.0
    max_temp_threshold: float = 36.0
    rainfall_min_mm: float = 100.0
    rainfall_max_mm: float = 300.0
    pest_susceptibility: str = "Medium"
    growth_duration_days: int = 140
    yield_potential_ton_ha: float = 6.0
    description_bn: Optional[str] = None

class VarietyCreate(VarietyBase):
    pass

class VarietyResponse(VarietyBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

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
    temperature: float = 28.0  # °C
    humidity: float = 75.0     # %
    rainfall: float = 150.0    # mm
    wind_speed: float = 12.0   # km/h
    pest_density: float = 15.0  # insects/m2

class RiskEvaluationResult(BaseModel):
    variety_id: int
    variety_name: str
    variety_name_bangla: str
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    overall_risk_score: float  # 0 to 100
    metric_scores: Dict[str, float]
    metric_levels: Dict[str, str]
    triggered_warnings: List[str]
    scenario: WeatherScenario

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

class ForecastPoint(BaseModel):
    ds: str
    yhat: float
    yhat_lower: float
    yhat_upper: float

class ForecastResponse(BaseModel):
    variety_id: int
    metric_type: str
    points: List[ForecastPoint]
