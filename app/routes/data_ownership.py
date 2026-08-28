from fastapi import APIRouter, HTTPException

from app.schemas.data_ownership_schema import UserData, DeleteResponse, DeleteRequest
from app.services import data_ownership_service

router = APIRouter()

@router.get("/my_data", response_model=UserData)
def get_my_data(user_id = 1):
    return data_ownership_service.get_user_data(user_id)

@router.delete("/delete",response_model=DeleteResponse)
def delete_data(request: DeleteRequest, user_id:int = 1):
    success = data_ownership_service.delete_data(request,user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Delete Failed")
    return DeleteResponse(success=True, message=f"{request.data_type} deleted successfully")