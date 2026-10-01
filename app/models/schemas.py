from pydantic import BaseModel


class PredictionRequest(BaseModel):
    crop: str
    region: str
    variety: str = "HYV"
    cropping_type: str = "single"


class PredictionResponse(BaseModel):
    predicted_yield: float
    lower_bound: float
    upper_bound: float
    message: str
    model_version: str
    cache_hit: bool