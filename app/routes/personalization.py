from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.personalization import (
    PreferenceResponse,
    SavePreferenceRequest,
    SaveResponse,
)
from app.services.auth_service import get_current_user, get_optional_current_user
from app.services.personalization_service import get_user_preferences, save_preference

router = APIRouter()


@router.post("/save", response_model=SaveResponse)
def save_preferences(
    request: SavePreferenceRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    user_id = current_user.id if current_user else request.user_id
    try:
        save_preference(user_id, request.crop, request.region, db)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save preferences: {exc}") from exc
    return SaveResponse(success=True, message="Preferences saved")


@router.get("/me", response_model=PreferenceResponse)
def get_my_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_user_preferences(current_user.id, db)


@router.get("/{user_id}", response_model=PreferenceResponse)
def get_user_preferences_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    target_id = current_user.id if current_user else user_id
    return get_user_preferences(target_id, db)
