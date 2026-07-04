from datetime import datetime

from fastapi import APIRouter

from app.core.memory import EternalMemory
from app.models.session import SessionSummary

router = APIRouter()


@router.get("/sessions/{user_id}", response_model=list[SessionSummary])
async def list_sessions(user_id: str):
    memory = EternalMemory(user_id)
    results = await memory.recall_context("list all sessions", top_k=50)
    sessions = []
    for r in results:
        meta = r.get("metadata", {})
        ts = r.get("created_at", datetime.utcnow().isoformat())
        try:
            timestamp = datetime.fromisoformat(ts)
        except (ValueError, TypeError):
            timestamp = datetime.utcnow()
        sessions.append(
            SessionSummary(
                session_id=r.get("id", ""),
                timestamp=timestamp,
                mood_score=meta.get("mood"),
                topics=meta.get("topics", []),
            )
        )
    return sessions
