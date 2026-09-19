from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from app.database import Base


class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, index=True)

    crop = Column(String(100), nullable=False)
    region = Column(String(100), nullable=False)
    variety = Column(String(50), nullable=False)
    cropping_type = Column(String(50), nullable=False)

    predicted_yield = Column(Float, nullable=False)
    lower_bound = Column(Float, nullable=False)
    upper_bound = Column(Float, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)