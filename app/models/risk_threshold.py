from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database import Base


class RiskThreshold(Base):
    __tablename__ = "risk_thresholds"

    id = Column(Integer, primary_key=True, index=True)
    crop = Column(String(100), nullable=False, index=True)        # e.g. "Rice", "Wheat", "Potato", "All"
    region = Column(String(100), nullable=True, default="All")    # e.g. "Rangpur", "Khulna", "All"
    metric = Column(String(100), nullable=False)                  # e.g. "predicted_yield_min", "yield_ratio_to_norm", "ndvi_min"
    
    # Threshold cutoffs
    low_threshold = Column(Float, nullable=False)                 # Value above this is Low risk
    medium_threshold = Column(Float, nullable=False)              # Value between medium and low is Medium risk
    high_threshold = Column(Float, nullable=False)                # Value below this is High risk (or above if inverse metric)
    
    unit = Column(String(50), nullable=False, default="ton/ha")
    description_bn = Column(String(255), nullable=True)
    description_en = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
