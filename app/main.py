from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat, sessions, journal, privacy

app = FastAPI(
    title="The Eternal Therapist",
    description="AI therapy companion with persistent memory via Cognee Cloud",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, tags=["Chat"])
app.include_router(sessions.router, tags=["Sessions"])
app.include_router(journal.router, tags=["Journal"])
app.include_router(privacy.router, tags=["Privacy"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "Eternal Therapist"}
