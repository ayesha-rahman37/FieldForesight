from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models.crop_variety import CropVariety
from app.scripts.seed_samir_data import DEFAULT_VARIETIES, seed_samir_data

router = APIRouter()


class VarietyResponse(BaseModel):
    id: int
    crop: str
    variety_code: str
    name_en: str
    name_bn: str
    variety_type: str
    yield_coefficient: float
    potential_yield_min: Optional[float] = None
    potential_yield_max: Optional[float] = None
    maturity_days: Optional[int] = None
    season: Optional[str] = None
    stress_tolerance: Optional[str] = None
    description_bn: Optional[str] = None
    description_en: Optional[str] = None
    is_recommended: bool

    class Config:
        from_attributes = True


@router.get("/varieties", response_model=List[VarietyResponse])
def get_varieties(
    crop: Optional[str] = Query(None, description="Filter varieties by crop name, e.g. Rice"),
    season: Optional[str] = Query(None, description="Filter by season, e.g. Boro, Aman"),
    stress: Optional[str] = Query(None, description="Filter by stress tolerance: Saline, Drought, Submergence"),
    db: Session = Depends(get_db),
):
    # Ensure seed data exists if table is empty
    count = db.query(CropVariety).count()
    if count == 0:
        seed_samir_data()

    query = db.query(CropVariety)
    if crop and crop.strip():
        query = query.filter(CropVariety.crop.ilike(f"%{crop.strip()}%"))
    if season and season.strip():
        query = query.filter((CropVariety.season.ilike(f"%{season.strip()}%")) | (CropVariety.season == "All"))
    if stress and stress.strip():
        query = query.filter(CropVariety.stress_tolerance.ilike(f"%{stress.strip()}%"))

    varieties = query.order_by(CropVariety.is_recommended.desc(), CropVariety.yield_coefficient.desc()).all()
    return varieties


@router.get("/varieties/recommendations", response_model=List[VarietyResponse])
def get_variety_recommendations(
    crop: str = Query("Rice"),
    region: str = Query("Rangpur"),
    db: Session = Depends(get_db),
):
    """
    Returns smart certified seed variety recommendations matching regional climate traits:
    - Coastal regions get Salt-Tolerant varieties
    - Barind / North gets Drought-Tolerant / Short Duration varieties
    - Haor gets Early Flash-Flood / High Yield Boro varieties
    """
    count = db.query(CropVariety).count()
    if count == 0:
        seed_samir_data()

    region_lower = region.lower()
    stress_tag = None
    if any(r in region_lower for r in ["khulna", "barishal", "satkhira", "patuakhali", "barguna"]):
        stress_tag = "Saline"
    elif any(r in region_lower for r in ["rajshahi", "rangpur", "dinajpur", "bogura", "naogaon"]):
        stress_tag = "Drought"
    elif any(r in region_lower for r in ["sylhet", "sunamganj", "netrokona"]):
        stress_tag = "Submergence"

    query = db.query(CropVariety).filter(CropVariety.crop.ilike(crop.strip()))
    if stress_tag:
        recommended = query.filter(
            (CropVariety.stress_tolerance == stress_tag) | (CropVariety.is_recommended == True)
        ).order_by(
            (CropVariety.stress_tolerance == stress_tag).desc(),
            CropVariety.yield_coefficient.desc(),
        ).limit(4).all()
        return recommended

    return query.filter(CropVariety.is_recommended == True).order_by(CropVariety.yield_coefficient.desc()).limit(4).all()


@router.get("/varieties/{variety_code}", response_model=VarietyResponse)
def get_variety_detail(
    variety_code: str,
    db: Session = Depends(get_db),
):
    variety = (
        db.query(CropVariety)
        .filter(CropVariety.variety_code.ilike(variety_code.strip()))
        .first()
    )
    if not variety:
        raise HTTPException(status_code=404, detail="Crop variety not found")
    return variety
