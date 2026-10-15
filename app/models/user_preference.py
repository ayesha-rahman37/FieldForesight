import datetime

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime

from app.database import Base


class UserPreference(Base):
    __tablename__ = "user_preference"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer,nullable=False, index=True)
    last_crop = Column(String(50),nullable=True)
    last_region = Column(String(50), nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)