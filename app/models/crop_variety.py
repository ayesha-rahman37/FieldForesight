from sqlalchemy import Column, Integer, String, Float, Text, Boolean, UniqueConstraint
from app.database import Base


class CropVariety(Base):
    __tablename__ = "crop_varieties"

    id = Column(Integer, primary_key=True, index=True)
    crop = Column(String(100), nullable=False, index=True)               # e.g. "Rice", "Wheat", "Potato"
    variety_code = Column(String(100), nullable=False, index=True)       # e.g. "BRRI_DHAN_28", "HYV", "Local"
    name_en = Column(String(100), nullable=False)                       # e.g. "BRRI dhan28"
    name_bn = Column(String(100), nullable=False)                       # e.g. "ব্রি ধান২৮"
    variety_type = Column(String(50), nullable=False, default="HYV")     # 'HYV', 'Hybrid', 'Local', 'Stress-Tolerant'

    yield_coefficient = Column(Float, nullable=False, default=1.0)       # Yield adjustment multiplier
    potential_yield_min = Column(Float, nullable=True)                   # Minimum expected yield (ton/ha)
    potential_yield_max = Column(Float, nullable=True)                   # Maximum potential yield (ton/ha)
    maturity_days = Column(Integer, nullable=True)                       # Days to maturity
    season = Column(String(50), nullable=True, default="All")            # 'Boro', 'Aman', 'Aus', 'Rabi', 'Kharif', 'All'
    stress_tolerance = Column(String(100), nullable=True)                # 'Drought', 'Saline', 'Submergence', 'Cold', 'Standard'

    description_bn = Column(Text, nullable=True)
    description_en = Column(Text, nullable=True)
    is_recommended = Column(Boolean, default=True)

    __table_args__ = (
        UniqueConstraint('crop', 'variety_code', name='uix_crop_variety_code'),
    )
