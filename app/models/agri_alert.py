from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class AgriAlert(Base):
    __tablename__ = "agri_alerts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    source_url = Column(String(500), unique=True, index=True, nullable=False)
    summary = Column(Text, nullable=True)
    district = Column(String(50), index=True, default="National")
    risk_tag = Column(String(50), default="General")
    crawled_at = Column(DateTime, default=_utcnow, nullable=False)

