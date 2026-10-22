from typing import List, Optional

from pydantic import BaseModel

class PredictionHistoryItem(BaseModel):
    prediction_id: str
    date: str
    crop: str
    region: str
    variety: str = "HYV"
    yield_predicted: str
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None

class UserProfileData(BaseModel):
    name: str
    phone: str = ""
    region: str = ""
    username: str = ""
    email: str = ""
    role: str = "farmer"
    created_at: str = ""

class UserData(BaseModel):
    profile: UserProfileData
    prediction_history: List[PredictionHistoryItem]
    prediction_count: int = 0
    saved_preference: dict
    preferences_count: int = 0

class DeleteRequest(BaseModel):
    data_type: str

class DeleteResponse(BaseModel):
    success: bool
    message: str