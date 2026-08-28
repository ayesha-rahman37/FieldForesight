from fastapi import APIRouter, Depends
from requests import Session


from app.database import get_db
from app.schemas.personalization import SaveResponse, SavePreferenceRequest, PreferenceResponse
from app.services.personalization_service import save_preference, get_user_references

router = APIRouter()

@router.post("/save", response_model=SaveResponse)
def save_preferences(request: SavePreferenceRequest, db:Session=Depends(get_db)):
    save_preference(request.user_id, request.crop,request.region,db)
    return SaveResponse(success=True,message="Preferences saved")

@router.get("/{user_id}", response_model=PreferenceResponse)
def get_references(user_id:int, db:Session=Depends(get_db)):
    return  get_user_references(user_id,db)