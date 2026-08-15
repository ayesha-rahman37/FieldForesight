from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

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
