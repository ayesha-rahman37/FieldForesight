from fastapi import APIRouter
from app.models.schemas import PredictionRequest, PredictionResponse
from app.services.prediction_service import get_prediction

router = APIRouter()

@router.post("/predict", response_model=PredictionResponse)
def predict_yield(data: PredictionRequest):
    result = get_prediction(data.crop, data.region, data.variety)
    return result