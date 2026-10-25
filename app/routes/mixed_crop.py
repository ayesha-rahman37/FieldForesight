from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.crop import Crop
from app.models.mixed_cropping import MixedCroppingMapping
from app.scripts.load_data import CROP_TYPE_MAP, get_or_create_crop

router = APIRouter()


class MixedCropItem(BaseModel):
    crop: str
    sequence_order: int | None = None


class MixedCropRequest(BaseModel):
    farm_id: str
    relation_type: str  # "rotation" or "intercrop"
    crops: List[MixedCropItem]


@router.post("/mixed-crop")
def save_mixed_crop(payload: MixedCropRequest, db: Session = Depends(get_db)):
    saved = []

    try:
        for item in payload.crops:
            clean_name = item.crop.strip()
            crop_obj = db.query(Crop).filter(Crop.name.ilike(clean_name)).first()
            if not crop_obj and clean_name.lower() in CROP_TYPE_MAP:
                crop_obj = get_or_create_crop(db, clean_name, CROP_TYPE_MAP[clean_name.lower()])
            if not crop_obj:
                raise HTTPException(status_code=404, detail=f"Crop '{item.crop}' পাওয়া যায়নি।")

            mapping = MixedCroppingMapping(
                farm_id=payload.farm_id,
                crop_id=crop_obj.id,
                sequence_order=item.sequence_order,
                relation_type=payload.relation_type,
            )
            db.add(mapping)
            saved.append(crop_obj.name)

        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save mixed cropping: {exc}") from exc

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
            "crop": m.crop.name if m.crop else "Unknown",
            "sequence_order": m.sequence_order,
            "relation_type": m.relation_type,
        }
        for m in mappings
    ]
