from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.data.district_coordinates import normalize_region_name
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
    if not data.crop or not data.crop.strip() or not data.region or not data.region.strip():
        raise HTTPException(status_code=400, detail="Crop and region parameters must not be empty.")

    clean_crop = data.crop.strip().title()
    canonical_region = normalize_region_name(data.region)

    try:
        result = get_prediction(
            crop=clean_crop,
            region=canonical_region,
            variety=data.variety,
            cropping_type=data.cropping_type,
            db=db,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        history = PredictionHistory(
            user_id=current_user.id if current_user else None,
            crop=clean_crop,
            region=canonical_region,
            variety=data.variety,
            cropping_type=data.cropping_type,
            predicted_yield=result["predicted_yield"],
            lower_bound=result["lower_bound"],
            upper_bound=result["upper_bound"],
        )
        db.add(history)
        db.commit()
        db.refresh(history)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to persist prediction history: {exc}") from exc

    return {**result, "prediction_id": history.id}
