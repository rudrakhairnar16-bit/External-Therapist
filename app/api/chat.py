from fastapi import APIRouter, HTTPException

from app.core.llm import TherapyLLM
from app.models.session import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.user_id or not request.message.strip():
        raise HTTPException(status_code=400, detail="user_id and message are required")
    llm = TherapyLLM(request.user_id)
    try:
        reply = await llm.respond(request.message)
        return ChatResponse(reply=reply, user_id=request.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
