from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.database import Base
import datetime


class UserSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow
    )