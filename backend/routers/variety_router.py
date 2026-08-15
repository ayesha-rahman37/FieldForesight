from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Variety
from schemas import VarietyResponse, VarietyCreate

router = APIRouter(prefix="/api/varieties", tags=["Varieties"])


@router.get("", response_model=List[VarietyResponse])
def list_varieties(db: Session = Depends(get_db)):
    return db.query(Variety).all()


@router.get("/{variety_id}", response_model=VarietyResponse)
def get_variety(variety_id: int, db: Session = Depends(get_db)):
    v = db.query(Variety).filter(Variety.id == variety_id).first()
    if not v:
        raise HTTPException(status_code=404, detail=f"Variety with ID {variety_id} not found")
    return v


@router.post("", response_model=VarietyResponse)
def create_variety(variety_in: VarietyCreate, db: Session = Depends(get_db)):
    v = Variety(**variety_in.model_dump())
    try:
        db.add(v)
        db.commit()
        db.refresh(v)
        return v
    except Exception as err:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create variety: {str(err)}")
