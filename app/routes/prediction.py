from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.prediction_history import PredictionHistory
from app.models.schemas import PredictionRequest, PredictionResponse
from app.models.user import User
from app.services.auth_service import get_current_user
from app.services.prediction_service import get_prediction


router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
def predict_yield(
    data: PredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = get_prediction(
        data.crop,
        data.region,
        data.variety,
        data.cropping_type
    )

    history = PredictionHistory(
        user_id=current_user.id,
        crop=data.crop,
        region=data.region,
        variety=data.variety,
        cropping_type=data.cropping_type,
        predicted_yield=result["predicted_yield"],
        lower_bound=result["lower_bound"],
        upper_bound=result["upper_bound"]
    )

    db.add(history)
    db.commit()

    return result