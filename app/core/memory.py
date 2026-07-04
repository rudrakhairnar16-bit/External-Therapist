import asyncio
import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx

from app.core import config

SQLITE_PATH = Path(__file__).resolve().parent.parent.parent / "external_therapist.db"
API_BASE = f"{config.COGNEE_BASE_URL}/api/v1"
HEADERS = {"X-Api-Key": config.COGNEE_API_KEY}
SSL_VERIFY = config.COGNEE_VERIFY_SSL

TIMEOUT_LONG = 60
TIMEOUT_SHORT = 15


def _init_sqlite():
    conn = sqlite3.connect(str(SQLITE_PATH))
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


def _sqlite_remember(user_id: str, content: str, metadata: str) -> str:
    conn = sqlite3.connect(str(SQLITE_PATH))
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


def _sqlite_recall(user_id: str, top_k: int) -> list[dict[str, Any]]:
    conn = sqlite3.connect(str(SQLITE_PATH))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """SELECT id, memory_type, content, metadata, created_at
           FROM memories WHERE user_id = ?
           ORDER BY created_at DESC LIMIT ?""",
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


def _sqlite_delete_all(user_id: str):
    conn = sqlite3.connect(str(SQLITE_PATH))
    conn.execute("DELETE FROM memories WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def _sqlite_delete_memory(user_id: str, memory_id: str):
    conn = sqlite3.connect(str(SQLITE_PATH))
    conn.execute("DELETE FROM memories WHERE id = ? AND user_id = ?", (memory_id, user_id))
    conn.commit()
    conn.close()


_init_sqlite()


class EternalMemory:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.dataset_name = f"therapy_{user_id}"
        self._mode = "unknown"

    async def _detect_mode(self):
        if self._mode != "unknown":
            return self._mode
        if not config.COGNEE_API_KEY:
            self._mode = "sqlite"
            return self._mode
        try:
            async with httpx.AsyncClient(verify=SSL_VERIFY) as client:
                resp = await client.get(
                    f"{API_BASE}/health", headers=HEADERS, timeout=10
                )
                if resp.is_success:
                    self._mode = "cloud"
                else:
                    self._mode = "sqlite"
        except Exception:
            self._mode = "sqlite"
        return self._mode

    async def _run_sqlite(self, fn, *args):
        return await asyncio.to_thread(fn, *args)

    async def remember(self, content: str, metadata: dict | None = None) -> str:
        mode = await self._detect_mode()
        if mode == "sqlite":
            return await self._run_sqlite(
                _sqlite_remember, self.user_id, content, json.dumps(metadata or {})
            )
        text = content
        if metadata:
            text = f"{content}\n\nMETADATA: {json.dumps(metadata)}"
        content_bytes = text.encode("utf-8")
        files = {"data": ("memory.txt", content_bytes, "text/plain")}
        data = {"datasetName": self.dataset_name}
        async with httpx.AsyncClient(verify=SSL_VERIFY) as client:
            resp = await client.post(
                f"{API_BASE}/remember",
                data=data,
                files=files,
                headers=HEADERS,
                timeout=TIMEOUT_LONG,
            )
            resp.raise_for_status()
            result = resp.json()
            return result.get("id", str(uuid.uuid4()))

    async def recall(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        mode = await self._detect_mode()
        if mode == "sqlite":
            return await self._run_sqlite(_sqlite_recall, self.user_id, top_k)
        async with httpx.AsyncClient(verify=SSL_VERIFY) as client:
            resp = await client.post(
                f"{API_BASE}/recall",
                json={
                    "query": query,
                    "datasets": [self.dataset_name],
                    "topK": top_k,
                    "searchType": "GRAPH_COMPLETION",
                },
                headers=HEADERS,
                timeout=TIMEOUT_SHORT,
            )
            if resp.status_code == 422:
                return []
            resp.raise_for_status()
            results = resp.json()
        parsed = []
        for r in results if isinstance(results, list) else []:
            if r.get("source") == "graph":
                parsed.append(
                    {
                        "id": r.get("dataset_id", str(uuid.uuid4())),
                        "type": "graph",
                        "content": r.get("text", ""),
                        "metadata": r.get("metadata", {}),
                        "score": r.get("score", 0),
                        "created_at": "",
                    }
                )
        return parsed

    async def recall_formatted(self, query: str, top_k: int = 5) -> str:
        results = await self.recall(query, top_k=top_k)
        if not results:
            return "No previous memories found."
        parts = []
        for i, r in enumerate(results, 1):
            content = r.get("content", "")[:300]
            parts.append(f"[{i}] {content}")
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
        await self.improve()

    async def improve(self):
        mode = await self._detect_mode()
        if mode == "sqlite":
            return
        async with httpx.AsyncClient(verify=SSL_VERIFY) as client:
            try:
                await client.post(
                    f"{API_BASE}/improve",
                    json={"datasetName": self.dataset_name, "runInBackground": True},
                    headers=HEADERS,
                    timeout=TIMEOUT_SHORT,
                )
            except Exception:
                pass

    async def delete_all(self):
        mode = await self._detect_mode()
        if mode == "sqlite":
            await self._run_sqlite(_sqlite_delete_all, self.user_id)
            return
        async with httpx.AsyncClient(verify=SSL_VERIFY) as client:
            try:
                resp = await client.get(
                    f"{API_BASE}/datasets",
                    headers=HEADERS,
                    timeout=TIMEOUT_SHORT,
                )
                if resp.is_success:
                    datasets = resp.json()
                    for ds in datasets if isinstance(datasets, list) else []:
                        if ds.get("name") == self.dataset_name:
                            await client.delete(
                                f"{API_BASE}/datasets/{ds['id']}",
                                headers=HEADERS,
                                timeout=TIMEOUT_SHORT,
                            )
            except Exception:
                pass

    async def delete_memory(self, memory_id: str):
        mode = await self._detect_mode()
        if mode == "sqlite":
            await self._run_sqlite(_sqlite_delete_memory, self.user_id, memory_id)
            return
        pass

    async def forget(self, memory_id: str | None = None):
        if memory_id:
            await self.delete_memory(memory_id)
        else:
            await self.delete_all()
