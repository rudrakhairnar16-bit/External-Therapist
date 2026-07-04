import json
import uuid
from typing import Any

import httpx

from app.core import config

API_BASE = f"{config.COGNEE_BASE_URL}/api/v1"
HEADERS = {"X-Api-Key": config.COGNEE_API_KEY}

TIMEOUT_ADD = 60
TIMEOUT_RECALL = 30
TIMEOUT_DATASET = 15


class EternalMemory:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.dataset_name = f"therapy_{user_id}"

    async def remember(self, content: str, metadata: dict | None = None) -> str:
        text = content
        if metadata:
            text = f"{content}\n\nMETADATA: {json.dumps(metadata)}"

        content_bytes = text.encode("utf-8")
        files = {"data": ("memory.txt", content_bytes, "text/plain")}
        data = {"datasetName": self.dataset_name}

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{API_BASE}/remember",
                data=data,
                files=files,
                headers=HEADERS,
                timeout=TIMEOUT_ADD,
            )
            resp.raise_for_status()
            result = resp.json()
            return result.get("id", str(uuid.uuid4()))

    async def recall(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{API_BASE}/recall",
                json={
                    "query": query,
                    "datasets": [self.dataset_name],
                    "topK": top_k,
                    "searchType": "GRAPH_COMPLETION",
                },
                headers=HEADERS,
                timeout=TIMEOUT_RECALL,
            )
            if resp.status_code == 422:
                return []
            resp.raise_for_status()
            results = resp.json()

        parsed = []
        for r in results if isinstance(results, list) else []:
            source = r.get("source", "")
            if source == "graph":
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
        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    f"{API_BASE}/improve",
                    json={"datasetName": self.dataset_name, "runInBackground": True},
                    headers=HEADERS,
                    timeout=TIMEOUT_RECALL,
                )
            except Exception:
                pass

    async def delete_memory(self, memory_id: str):
        pass

    async def delete_all(self):
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{API_BASE}/datasets",
                    headers=HEADERS,
                    timeout=TIMEOUT_DATASET,
                )
                if resp.is_success:
                    datasets = resp.json()
                    for ds in datasets if isinstance(datasets, list) else []:
                        if ds.get("name") == self.dataset_name:
                            await client.delete(
                                f"{API_BASE}/datasets/{ds['id']}",
                                headers=HEADERS,
                                timeout=TIMEOUT_DATASET,
                            )
            except Exception:
                pass

    async def forget(self, memory_id: str | None = None):
        if memory_id:
            await self.delete_memory(memory_id)
        else:
            await self.delete_all()
