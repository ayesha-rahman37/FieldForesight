from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from app.database import Base

class MixedCroppingMapping(Base):
    __tablename__ = "mixed_cropping_mappings"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(String, nullable=False)        # farm/user কে চিহ্নিত করার id
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False)
    sequence_order = Column(Integer, nullable=True) # rotation হলে ক্রম (1st crop, 2nd crop...)
    relation_type = Column(String, nullable=True)   # "rotation" বা "intercrop"

    crop = relationship("Crop")