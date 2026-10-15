from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.data_ownership_schema import UserData, DeleteResponse, DeleteRequest
from app.services import data_ownership_service

from app.models.user import User
from app.services.auth_service import get_current_user, get_optional_current_user

router = APIRouter()


@router.get("/my_data", response_model=UserData)
def get_my_data(
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else 1
    return data_ownership_service.get_user_data(user_id, db)


@router.delete("/delete", response_model=DeleteResponse)
def delete_data(
    request: DeleteRequest,
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    user_id = current_user.id if current_user else 1
    success = data_ownership_service.delete_data(request, user_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="No data found to delete")
    return DeleteResponse(success=True, message=f"{request.data_type} deleted successfully")