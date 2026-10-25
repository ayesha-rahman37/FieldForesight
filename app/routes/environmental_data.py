from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.data_fusion_service import get_regional_environmental_data

router = APIRouter()


@router.get("/{region}")
def regional_environmental_data(
    region: str,
    start_year: int = Query(default=2020, ge=2000, le=2100),
    end_year: int = Query(default=2025, ge=2000, le=2100),
    db: Session = Depends(get_db),
):
    if start_year > end_year:
        raise HTTPException(
            status_code=400,
            detail="start_year must be less than or equal to end_year",
        )

    return get_regional_environmental_data(
        region=region,
        start_year=start_year,
        end_year=end_year,
        db=db,
    )
