from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class HistoricalYield(Base):
    __tablename__ = "historical_yields"

    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    year = Column(Integer, nullable=False)
    rainfall = Column(Float, nullable=True)     # mm
    yield_value = Column(Float, nullable=False) # ton/hectare

    crop = relationship("Crop")
    region = relationship("Region")