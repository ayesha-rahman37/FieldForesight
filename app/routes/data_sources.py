from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.data_source_status import get_data_source_status

router = APIRouter()


@router.get("/status")
def data_source_status(db: Session = Depends(get_db)):
    return get_data_source_status(db)