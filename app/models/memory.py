from pydantic import BaseModel


class JournalEntry(BaseModel):
    user_id: str
    content: str
    mood_score: int | None = None
    tags: list[str] = []


class ForgetRequest(BaseModel):
    user_id: str
    memory_ids: list[str]


class InsightResponse(BaseModel):
    mood_trend: str
    common_topics: list[str]
    progress_notes: str
