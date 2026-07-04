from pydantic import BaseModel
from datetime import datetime


class UserCreate(BaseModel):
    user_id: str


class UserResponse(BaseModel):
    user_id: str
    created_at: datetime
    session_count: int
