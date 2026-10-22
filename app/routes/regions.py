from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.data.district_coordinates import CANONICAL_DISTRICT_COORDINATES
from app.database import get_db
from app.models.region import Region
from app.scripts.load_data import get_or_create_region

router = APIRouter()


@router.get("/regions")
def get_regions(db: Session = Depends(get_db)):
    regions = db.query(Region).order_by(Region.id.asc()).all()
    if len(regions) < len(CANONICAL_DISTRICT_COORDINATES):
        for district_name in CANONICAL_DISTRICT_COORDINATES:
            get_or_create_region(db, district_name)
        db.commit()
        regions = db.query(Region).order_by(Region.id.asc()).all()

    return [
        {
            "id": region.id,
            "name": region.name,
        }
        for region in regions
    ]
