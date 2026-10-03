from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.prediction_history import PredictionHistory
from app.models.user import User
from app.services.auth_service import get_current_user


router = APIRouter()


@router.get("/predictions/history")
def get_prediction_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    predictions = (
        db.query(PredictionHistory)
        .filter(PredictionHistory.user_id == current_user.id)
        .order_by(PredictionHistory.created_at.desc())
        .all()
    )

    return [
        {
            "id": prediction.id,
            "crop": prediction.crop,
            "region": prediction.region,
            "variety": prediction.variety,
            "cropping_type": prediction.cropping_type,
            "predicted_yield": prediction.predicted_yield,
            "lower_bound": prediction.lower_bound,
            "upper_bound": prediction.upper_bound,
            "created_at": prediction.created_at.isoformat()
        }
        for prediction in predictions
    ]