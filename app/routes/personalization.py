from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.personalization import (
    SaveResponse,
    SavePreferenceRequest,
    PreferenceResponse,
)
from app.services.auth_service import get_current_user
from app.services.personalization_service import (
    save_preference,
    get_user_references,
)

router = APIRouter()


@router.post("/save", response_model=SaveResponse)
def save_preferences(
    request: SavePreferenceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    save_preference(
        current_user.id, request.crop, request.region, db
    )
    return SaveResponse(
        success=True,
        message="Preferences saved",
    )


@router.get("/{user_id}", response_model=PreferenceResponse)
def get_references(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if user_id != current_user.id:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=403,
            detail="Cannot access another user's preferences",
        )

    return get_user_references(current_user.id, db)