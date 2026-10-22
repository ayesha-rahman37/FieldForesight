from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from app.database import Base


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class ModelMetadata(Base):
    __tablename__ = "model_metadata"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(100), nullable=False)
    crop = Column(String(100), nullable=False)
    region = Column(String(100), nullable=False)
    model_path = Column(String(255), nullable=False)
    training_records = Column(Integer, nullable=False)
    mae = Column(Float, nullable=True)
    rmse = Column(Float, nullable=True)
    mape = Column(Float, nullable=True)
    recent_weighting_enabled = Column(Boolean, default=True, nullable=False)
    trained_at = Column(DateTime, default=_utcnow, nullable=False)
