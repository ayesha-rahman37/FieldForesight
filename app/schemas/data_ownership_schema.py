from typing import Any, List
from pydantic import BaseModel


class PredictionHistoryItem(BaseModel):
    prediction_id: str
    date: str
    crop: str
    region: str
    yield_predicted: str


class UserProfileData(BaseModel):
    username: str
    email: str


class UserData(BaseModel):
    profile: UserProfileData
    prediction_history: List[PredictionHistoryItem]
    saved_preference: dict[str, Any]


class DeleteRequest(BaseModel):
    data_type: str


class DeleteResponse(BaseModel):
    success: bool
    message: str