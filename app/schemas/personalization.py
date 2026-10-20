from pydantic import BaseModel
from typing import Optional


class SavePreferenceRequest(BaseModel):
    crop: str
    region: str


class PreferenceResponse(BaseModel):
    user_id: int
    last_crop: Optional[str] = None
    last_region: Optional[str] = None


class SaveResponse(BaseModel):
    success: bool
    message: str