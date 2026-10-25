from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.crop import Crop
from app.scripts.load_data import DEFAULT_CROPS, get_or_create_crop

router = APIRouter()


@router.get("/crops")
def get_crops(db: Session = Depends(get_db)):
    crops = db.query(Crop).order_by(Crop.id.asc()).all()
    if len(crops) < len(DEFAULT_CROPS):
        for item in DEFAULT_CROPS:
            get_or_create_crop(db, item["name"], item["type"])
        db.commit()
        crops = db.query(Crop).order_by(Crop.id.asc()).all()

    return [
        {
            "id": crop.id,
            "name": crop.name,
            "type": crop.type or "cereal",
        }
        for crop in crops
    ]
