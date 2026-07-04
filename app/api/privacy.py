from fastapi import APIRouter, HTTPException

from app.core.memory import EternalMemory
from app.models.memory import ForgetRequest

router = APIRouter()


@router.post("/forget")
async def forget_memories(request: ForgetRequest):
    if not request.user_id or not request.memory_ids:
        raise HTTPException(status_code=400, detail="user_id and memory_ids are required")
    memory = EternalMemory(request.user_id)
    deleted = []
    for mid in request.memory_ids:
        try:
            await memory.delete_memory(mid)
            deleted.append(mid)
        except Exception:
            pass
    return {"deleted_count": len(deleted), "deleted_ids": deleted}


@router.post("/forget-all/{user_id}")
async def forget_all(user_id: str):
    memory = EternalMemory(user_id)
    await memory.delete_all()
    return {"status": "all memories deleted", "user_id": user_id}
