from pydantic import BaseModel
from typing import Optional

class SavePreferenceRequest(BaseModel):
    user_id: int
    crop: str
    region: str

class PreferenceResponse(BaseModel):
    user_id: int
    last_crop: Optional[str]
    last_region: Optional[str]

class SaveResponse(BaseModel):
    success: bool
    message: str