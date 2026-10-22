from typing import List, Optional
from pydantic import BaseModel, Field


class ChatContextPayload(BaseModel):
    crop: Optional[str] = None
    region: Optional[str] = None
    predicted_yield: Optional[float] = None


class ChatHistoryItem(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    conversation_id: Optional[str] = None
    history: Optional[List[ChatHistoryItem]] = None
    context: Optional[ChatContextPayload] = None


class ChatStreamRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    conversation_id: Optional[str] = None
    history: Optional[List[ChatHistoryItem]] = None
    context: Optional[ChatContextPayload] = None


class ChatResponse(BaseModel):
    reply: str
    conversation_id: str
    sources: List[str] = []

