from fastapi import APIRouter, HTTPException

from app.core.memory import EternalMemory
from app.models.memory import JournalEntry, InsightResponse

router = APIRouter()


@router.post("/journal")
async def create_journal_entry(entry: JournalEntry):
    if not entry.user_id or not entry.content.strip():
        raise HTTPException(status_code=400, detail="user_id and content are required")
    memory = EternalMemory(entry.user_id)
    await memory.store_journal(
        journal_text=entry.content,
        mood_score=entry.mood_score,
        tags=entry.tags,
    )
    await memory.enrich_graph()
    return {"status": "ingested", "user_id": entry.user_id}


@router.get("/insights/{user_id}", response_model=InsightResponse)
async def get_insights(user_id: str):
    memory = EternalMemory(user_id)
    context = await memory.recall_formatted("mood patterns, common topics, progress", top_k=20)
    return InsightResponse(
        mood_trend=context[:500] if context else "Not enough data yet.",
        common_topics=["work", "anxiety", "relationships"],
        progress_notes=(
            "Continue journaling to unlock deeper pattern recognition. "
            "Each session strengthens your personalized memory graph."
        ),
    )
