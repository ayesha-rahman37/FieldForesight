import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
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

class RiskThreshold(Base):
    __tablename__ = "risk_thresholds"

    id = Column(Integer, primary_key=True, index=True)
    variety_id = Column(Integer, ForeignKey("varieties.id"), nullable=False)
    metric_name = Column(String(50), nullable=False)  # temperature, humidity, rainfall, pest_density
    low_max = Column(Float, default=25.0)
    medium_max = Column(Float, default=32.0)
    high_max = Column(Float, default=36.0)
    critical_min = Column(Float, default=36.1)
    advisory_note_bn = Column(Text, nullable=True)

    variety = relationship("Variety", back_populates="thresholds")

class AdvisoryHistory(Base):
    __tablename__ = "advisory_histories"

    id = Column(Integer, primary_key=True, index=True)
    variety_id = Column(Integer, ForeignKey("varieties.id"), nullable=False)
    risk_level = Column(String(20), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    weather_scenario_json = Column(JSON, nullable=False)
    advisory_text_bn = Column(Text, nullable=False)
    action_items_json = Column(JSON, nullable=True)
    llm_provider = Column(String(50), default="Rule-Engine Fallback")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    variety = relationship("Variety", back_populates="advisories")

class ForecastData(Base):
    __tablename__ = "forecast_datas"

    id = Column(Integer, primary_key=True, index=True)
    variety_id = Column(Integer, ForeignKey("varieties.id"), nullable=False)
    metric_type = Column(String(50), default="yield_index")  # yield_index, heat_stress, pest_risk
    ds = Column(String(20), nullable=False)  # Date string YYYY-MM-DD
    yhat = Column(Float, nullable=False)
    yhat_lower = Column(Float, nullable=False)
    yhat_upper = Column(Float, nullable=False)

    variety = relationship("Variety", back_populates="forecasts")
