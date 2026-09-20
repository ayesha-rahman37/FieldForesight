from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.database import get_db
from app.models.crop import Crop
from app.models.mixed_cropping import MixedCroppingMapping

router = APIRouter()


class MixedCropItem(BaseModel):
    crop: str
    sequence_order: int | None = None


class MixedCropRequest(BaseModel):
    farm_id: str
    relation_type: str   # "rotation" বা "intercrop"
    crops: List[MixedCropItem]


@router.post("/mixed-crop")
def save_mixed_crop(payload: MixedCropRequest, db: Session = Depends(get_db)):
    saved = []

    for item in payload.crops:
        crop_obj = db.query(Crop).filter(Crop.name == item.crop).first()
        if not crop_obj:
            raise HTTPException(status_code=404, detail=f"Crop '{item.crop}' পাওয়া যায়নি।")

        mapping = MixedCroppingMapping(
            farm_id=payload.farm_id,
            crop_id=crop_obj.id,
            sequence_order=item.sequence_order,
            relation_type=payload.relation_type,
        )
        db.add(mapping)
        saved.append(item.crop)

    db.commit()
    return {"message": f"{len(saved)}টা crop mixed-cropping হিসেবে save হয়েছে।", "crops": saved}


@router.get("/mixed-crop/{farm_id}")
def get_mixed_crop(farm_id: str, db: Session = Depends(get_db)):
    mappings = (
        db.query(MixedCroppingMapping)
        .filter(MixedCroppingMapping.farm_id == farm_id)
        .order_by(MixedCroppingMapping.sequence_order.asc())
        .all()
    )

    return [
        {
            "crop": m.crop.name,
            "sequence_order": m.sequence_order,
            "relation_type": m.relation_type,
        }
        for m in mappings
    ]