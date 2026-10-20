from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.data_ownership_schema import (
    UserData,
    DeleteResponse,
    DeleteRequest,
)
from app.services import data_ownership_service
from app.services.auth_service import get_current_user

router = APIRouter()


@router.get("/my_data", response_model=UserData)
def get_my_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return data_ownership_service.get_user_data(current_user.id, db)
    except ValueError:
        raise HTTPException(status_code=404, detail="User not found")


@router.delete("/delete", response_model=DeleteResponse)
def delete_data(
    request: DeleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    success = data_ownership_service.delete_data(
        request, current_user.id, db
    )

    if not success:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported data_type. Use 'prediction_history' "
                "or 'preferences'."
            ),
        )

    return DeleteResponse(
        success=True,
        message=f"{request.data_type} deleted successfully",
    )