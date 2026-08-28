from pydantic import BaseModel

class ScenarioRequest(BaseModel):
    crop: str
    region: str
    variety: str = "HYV"
    cropping_type: str = "single"
    rainfall_adjustment_percent: float = 0.0   # -50 to +50 (slider value)

class ScenarioResponse(BaseModel):
    original_yield: float
    adjusted_yield: float
    lower_bound: float
    upper_bound: float
    adjustment_applied: float
    message: str