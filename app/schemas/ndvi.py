from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NDVIResponse(BaseModel):
    region: str
    vegetation_status: str
    ndvi_value: Optional[float] = None
    computed_at:  Optional[datetime] = None