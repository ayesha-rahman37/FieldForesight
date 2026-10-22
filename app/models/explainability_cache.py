from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from app.database import Base


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class ExplainabilityCache(Base):
    __tablename__ = "explainability_cache"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("prediction_history.id"), unique=True, nullable=False, index=True)
    crop = Column(String(50), nullable=False)
    region = Column(String(50), nullable=False)
    contributions = Column(JSON, nullable=False)
    top_factor = Column(String(50), nullable=False)
    summary_text_bn = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
