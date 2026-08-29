from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.ndvi import NDVIResponse
from app.services.ndvi_service import get_ndvi_for_region
router = APIRouter()


@router.get("/{region}", response_model=NDVIResponse)
def get_ndvi(region: str,db:Session = Depends(get_db)):
    return get_ndvi_for_region(region,db)
