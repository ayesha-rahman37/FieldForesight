from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.orm import relationship
from database import Base

class Variety(Base):
    __tablename__ = "varieties"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    name_bangla = Column(String(100), nullable=False)
    crop_type = Column(String(50), nullable=False)  # Boro Rice, Aman Rice, Wheat, Potato, etc.
    optimal_temp_min = Column(Float, default=20.0)
    optimal_temp_max = Column(Float, default=32.0)
    max_temp_threshold = Column(Float, default=36.0)
    rainfall_min_mm = Column(Float, default=100.0)
    rainfall_max_mm = Column(Float, default=300.0)
    pest_susceptibility = Column(String(20), default="Medium")  # Low, Medium, High
    growth_duration_days = Column(Integer, default=140)
    yield_potential_ton_ha = Column(Float, default=6.0)
    description_bn = Column(Text, nullable=True)

    thresholds = relationship("RiskThreshold", back_populates="variety", cascade="all, delete-orphan")
    advisories = relationship("AdvisoryHistory", back_populates="variety", cascade="all, delete-orphan")
    forecasts = relationship("ForecastData", back_populates="variety", cascade="all, delete-orphan")
