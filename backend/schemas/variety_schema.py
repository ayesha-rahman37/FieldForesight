from typing import Optional
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
