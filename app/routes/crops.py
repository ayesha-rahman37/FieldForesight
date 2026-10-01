from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.model_metadata import ModelMetadata


router = APIRouter()


@router.get("/crops")
def get_crops(
    db: Session = Depends(get_db)
):
    rows = (
        db.query(
            ModelMetadata.crop
        )
        .distinct()
        .order_by(
            ModelMetadata.crop
        )
        .all()
    )

    return [
        {
            "id": index + 1,
            "name": row[0],
            "type": "cereal"
        }
        for index, row in enumerate(rows)
    ]