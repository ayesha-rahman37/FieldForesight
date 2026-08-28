import datetime


from sqlalchemy import Column, Integer, String, JSON, DateTime

from app.database import Base


class ExplainabilityCache(Base):
    __tablename__ = 'explainability_cache'
    id = Column(Integer, primary_key=True)
    prediction_id = Column(Integer,unique=True)
    crop = Column(String(50),nullable=False)
    region = Column(String(50),nullable=False)
    contributions = Column(JSON,nullable=False)
    top_factor = Column(String(50),nullable=False)
    summary_text_bn = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)