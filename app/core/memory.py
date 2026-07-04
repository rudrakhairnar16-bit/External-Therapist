import asyncio
import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parent.parent.parent / "external_therapist.db"


def _run_sync(fn, *args, **kwargs):
    return asyncio.to_thread(fn, *args, **kwargs)


def _init_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        """CREATE TABLE IF NOT EXISTS memories (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            memory_type TEXT NOT NULL,
            content TEXT NOT NULL,
            metadata TEXT DEFAULT '{}',
            created_at TEXT NOT NULL
        )"""
    )
    conn.commit()
    conn.close()


def _sync_remember(user_id: str, content: str, metadata: str) -> str:
    conn = sqlite3.connect(str(DB_PATH))
    mem_id = str(uuid.uuid4())
    meta = json.loads(metadata)
    conn.execute(
        "INSERT INTO memories (id, user_id, memory_type, content, metadata, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (
            mem_id,
            user_id,
            meta.get("type", "memory"),
            content,
            metadata,
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    conn.close()
    return mem_id


def _sync_recall(user_id: str, top_k: int) -> list[dict[str, Any]]:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """SELECT id, memory_type, content, metadata, created_at
           FROM memories
           WHERE user_id = ?
           ORDER BY created_at DESC
           LIMIT ?""",
        (user_id, top_k),
    ).fetchall()
    conn.close()
    results = []
    for row in rows:
        results.append(
            {
                "id": row["id"],
                "type": row["memory_type"],
                "content": row["content"],
                "metadata": json.loads(row["metadata"]),
                "created_at": row["created_at"],
            }
        )
    return results


def _sync_delete_memory(user_id: str, memory_id: str | None = None):
    conn = sqlite3.connect(str(DB_PATH))
    if memory_id:
        conn.execute("DELETE FROM memories WHERE id = ? AND user_id = ?", (memory_id, user_id))
    else:
        conn.execute("DELETE FROM memories WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


_init_db()


class EternalMemory:
    def __init__(self, user_id: str):
        self.user_id = user_id

    async def remember(self, content: str, metadata: dict | None = None) -> str:
        return await _run_sync(_sync_remember, self.user_id, content, json.dumps(metadata or {}))

    async def recall(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        return await _run_sync(_sync_recall, self.user_id, top_k)

    async def recall_formatted(self, query: str, top_k: int = 5) -> str:
        results = await self.recall(query, top_k=top_k)
        if not results:
            return "No previous memories found."
        parts = []
        for i, r in enumerate(results, 1):
            ts = r.get("created_at", "unknown")
            content = r.get("content", "")
            parts.append(f"[{i}] ({ts}) {content[:300]}")
        return "\n".join(parts)

    async def recall_context(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        return await self.recall(query, top_k)

    async def store_session(self, transcript: str, mood_score: int, topics: list[str]) -> str:
        return await self.remember(
            transcript,
            metadata={"type": "session", "mood": mood_score, "topics": topics},
        )

    async def store_journal(self, journal_text: str, mood_score: int, tags: list[str]) -> str:
        return await self.remember(
            journal_text,
            metadata={"type": "journal", "mood": mood_score, "tags": tags},
        )

    async def enrich_graph(self):
        pass

    async def delete_memory(self, memory_id: str):
        await _run_sync(_sync_delete_memory, self.user_id, memory_id)

    async def delete_all(self):
        await _run_sync(_sync_delete_memory, self.user_id, None)

    async def improve(self):
        pass

    async def forget(self, memory_id: str | None = None):
        await _run_sync(_sync_delete_memory, self.user_id, memory_id)
