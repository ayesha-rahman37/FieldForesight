from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from app.database import Base


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class AdvisoryHistory(Base):
    __tablename__ = "advisory_history"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("prediction_history.id"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    crop = Column(String(100), nullable=False)
    region = Column(String(100), nullable=False)
    variety = Column(String(100), nullable=False, default="HYV")
    cropping_type = Column(String(50), nullable=False, default="single")

    predicted_yield = Column(Float, nullable=False)
    lower_bound = Column(Float, nullable=True)
    upper_bound = Column(Float, nullable=True)

    risk_level = Column(String(20), nullable=False, default="medium")  # 'low' | 'medium' | 'high'
    risk_score = Column(Float, nullable=False, default=50.0)           # 0.0 to 100.0

    advisory_text = Column(Text, nullable=False)                       # Bangla main advisory
    action_items = Column(Text, nullable=True)                         # JSON-serialized list of action steps in Bangla
    warning_alerts = Column(Text, nullable=True)                       # JSON-serialized warning alerts

    llm_provider = Column(String(50), nullable=False, default="groq")  # 'groq' | 'rule_engine'
    llm_model = Column(String(100), nullable=True, default="llama-3.3-70b-versatile")

    created_at = Column(DateTime, default=_utcnow, nullable=False)
