from pydantic import BaseModel
from datetime import datetime


class ChatRequest(BaseModel):
    user_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str
    user_id: str


class SessionSummary(BaseModel):
    session_id: str
    timestamp: datetime
    mood_score: int | None
    topics: list[str]
