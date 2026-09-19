from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.prediction_history import PredictionHistory


router = APIRouter()


@router.get("/predictions/history")
def get_prediction_history(
    db: Session = Depends(get_db)
):
    predictions = (
        db.query(PredictionHistory)
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