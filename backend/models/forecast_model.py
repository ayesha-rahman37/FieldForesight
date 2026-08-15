from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class ForecastData(Base):
    __tablename__ = "forecast_datas"

    id = Column(Integer, primary_key=True, index=True)
    variety_id = Column(Integer, ForeignKey("varieties.id"), nullable=False)
    metric_type = Column(String(50), default="yield_index")  # yield_index, heat_stress, pest_risk
    ds = Column(String(20), nullable=False)  # Date string YYYY-MM-DD
    yhat = Column(Float, nullable=False)
    yhat_lower = Column(Float, nullable=False)
    yhat_upper = Column(Float, nullable=False)

    variety = relationship("Variety", back_populates="forecasts")
