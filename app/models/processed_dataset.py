from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, Integer, String
from app.database import Base


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class ProcessedDataset(Base):
    __tablename__ = "processed_dataset"

    id = Column(Integer, primary_key=True, index=True)
    crop = Column(String(100), nullable=False)
    region = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    rainfall = Column(Float, nullable=True)
    yield_value = Column(Float, nullable=False)
    year_index = Column(Float, nullable=True)
    lag_yield = Column(Float, nullable=True)
    yield_change = Column(Float, nullable=True)
    rolling_yield_mean = Column(Float, nullable=True)
    yield_anomaly = Column(Float, nullable=True)
    anomaly_score = Column(Float, nullable=True)
    is_recent = Column(Integer, nullable=False, default=0)
    processed_at = Column(DateTime, default=_utcnow, nullable=False)
