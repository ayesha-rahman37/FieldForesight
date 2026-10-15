from sqlalchemy import Column,String,Integer,DateTime,Float

from app.database import Base


class NDVICache(Base):
    __tablename__ = "ndvi_cache"
    id = Column(Integer, primary_key=True)
    region_name = Column(String(50), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    ndvi_value = Column(Float, nullable=True)
    vegetation_status = Column(String(50), nullable=False,default="Pending")
    computed_at = Column(DateTime, nullable=True)