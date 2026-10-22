from sqlalchemy.orm import Session
from app.data.district_coordinates import normalize_region_name
from app.models.ndvi_cache import NDVICache
from app.schemas.ndvi import NDVIResponse


def get_ndvi_for_region(region_name: str, db: Session) -> NDVIResponse:
    canonical = normalize_region_name(region_name)
    record = (
        db.query(NDVICache)
        .filter(
            (NDVICache.region_name.ilike(canonical))
            | (NDVICache.region_name.ilike(region_name.strip()))
        )
        .order_by(NDVICache.computed_at.desc())
        .first()
    )
    if not record or record.ndvi_value is None:
        return NDVIResponse(
            region=region_name,
            vegetation_status="Unavailable (not yet computed)",
            ndvi_value=None,
            computed_at=None,
        )

    return NDVIResponse(
        region=region_name,
        vegetation_status=record.vegetation_status,
        ndvi_value=record.ndvi_value,
        computed_at=record.computed_at,
    )
