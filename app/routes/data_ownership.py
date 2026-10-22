from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.data_ownership_schema import DeleteRequest, DeleteResponse, UserData
from app.services import data_ownership_service
from app.services.auth_service import get_current_user

router = APIRouter()


@router.get("/my_data", response_model=UserData)
@router.get("/my-data", response_model=UserData, include_in_schema=False)
def get_my_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return data_ownership_service.get_user_data(current_user.id, db)


@router.delete("/delete", response_model=DeleteResponse)
def delete_user_data(
    request: DeleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    success = data_ownership_service.delete_data(request, current_user.id, db)
    if not success:
        raise HTTPException(status_code=404, detail="No data found to delete")
    return DeleteResponse(success=True, message=f"{request.data_type} deleted successfully")
