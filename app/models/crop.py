from sqlalchemy import Column, Integer, String
from app.database import Base

class Crop(Base):
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)   # e.g. "ধান", "গম"
    type = Column(String, nullable=True)                 # e.g. "cereal"