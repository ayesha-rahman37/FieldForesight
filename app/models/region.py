from sqlalchemy import Column, Integer, String
from app.database import Base

class Region(Base):
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)   # e.g. "Rangpur"