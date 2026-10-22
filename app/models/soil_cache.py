
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from app.database import Base


class SoilCache(Base):
    __tablename__ = "soil_cache"

    id = Column(Integer, primary_key=True, index=True)
    region_name = Column(String(100), nullable=False, unique=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    ph = Column(Float, nullable=True)
    organic_carbon = Column(Float, nullable=True)
    clay_content = Column(Float, nullable=True)
    sand_content = Column(Float, nullable=True)
    nitrogen = Column(Float, nullable=True)

    provider = Column(String(100), nullable=False, default="SoilGrids")
    status = Column(String(30), nullable=False, default="unavailable")
    fetched_at = Column(DateTime, nullable=True)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
