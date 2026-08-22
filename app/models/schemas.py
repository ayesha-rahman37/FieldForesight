from pydantic import BaseModel

class PredictionRequest(BaseModel):
    crop: str
    region: str
    variety: str = "HYV"          # "HYV" or "Local"
    cropping_type: str = "single"  # "single", "intercrop", or "rotation"

class PredictionResponse(BaseModel):
    predicted_yield: float
    lower_bound: float
    upper_bound: float
    message: str