from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.prediction_history import PredictionHistory
from app.models.schemas import (
    PredictionRequest,
    PredictionResponse
)
from app.services.prediction_service import get_prediction


from app.models.user import User
from app.services.auth_service import get_optional_current_user


router = APIRouter()


@router.post(
    "/predict",
    response_model=PredictionResponse
)
def predict_yield(
    data: PredictionRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    if not data.crop or not data.crop.strip() or not data.region or not data.region.strip():
        raise HTTPException(status_code=400, detail="Crop and region parameters must not be empty.")

    result = get_prediction(
        crop=data.crop,
        region=data.region,
        variety=data.variety,
        cropping_type=data.cropping_type,
        db=db
    )

    history = PredictionHistory(
        user_id=current_user.id if current_user else None,
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
    db.refresh(history)  # populate the auto-assigned id from SQLite

    return {**result, "prediction_id": history.id}