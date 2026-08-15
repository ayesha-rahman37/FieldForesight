import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base

class AdvisoryHistory(Base):
    __tablename__ = "advisory_histories"

    id = Column(Integer, primary_key=True, index=True)
    variety_id = Column(Integer, ForeignKey("varieties.id"), nullable=False)
    risk_level = Column(String(20), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    weather_scenario_json = Column(JSON, nullable=False)
    advisory_text_bn = Column(Text, nullable=False)
    action_items_json = Column(JSON, nullable=True)
    llm_provider = Column(String(50), default="Rule-Engine Fallback")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    variety = relationship("Variety", back_populates="advisories")
