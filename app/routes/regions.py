from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.model_metadata import ModelMetadata


router = APIRouter()


@router.get("/regions")
def get_regions(
    db: Session = Depends(get_db)
):
    rows = (
        db.query(
            ModelMetadata.region
        )
        .distinct()
        .order_by(
            ModelMetadata.region
        )
        .all()
    )

    return [
        {
            "id": index + 1,
            "name": row[0]
        }
        for index, row in enumerate(rows)
    ]