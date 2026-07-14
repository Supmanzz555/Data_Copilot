"""
HTTP client for Jina Embeddings API (https://api.jina.ai/v1/embeddings).
OpenAI-compatible request/response; uses retrieval.task types for RAG when supported.
"""
from __future__ import annotations

import asyncio
from functools import partial
from typing import Sequence

import httpx

from app.config import settings

_client: httpx.Client | None = None


def _get_client() -> httpx.Client:
    global _client
    if _client is None:
        _client = httpx.Client(timeout=120.0)
    return _client


def _request_payload(texts: Sequence[str], *, task: str | None) -> dict:
    body: dict = {
        "model": settings.JINA_EMBEDDINGS_MODEL,
        "input": list(texts),
        "normalized": True,
        "embedding_type": "float",
    }
    if task:
        body["task"] = task
    return body


def embed_texts_sync(texts: list[str], *, task: str | None = None) -> list[list[float]]:
    """
    Synchronous embedding call. Preserves input order (sorted by API index field).
    task: e.g. retrieval.passage for KB chunks, retrieval.query for user questions (jina-embeddings-v3+).
    """
    if not settings.JINA_API_KEY:
        raise ValueError("JINA_API_KEY is required for embeddings (set it in .env)")
    if not texts:
        return []

    headers = {
        "Authorization": f"Bearer {settings.JINA_API_KEY}",
        "Content-Type": "application/json",
    }
    url = settings.JINA_EMBEDDINGS_API_URL.rstrip("/")

    client = _get_client()
    resp = client.post(url, json=_request_payload(texts, task=task), headers=headers)
    resp.raise_for_status()
    payload = resp.json()

    items = payload.get("data") or []
    items.sort(key=lambda x: x.get("index", 0))
    vectors = [list(item["embedding"]) for item in items]

    expected = settings.JINA_EMBEDDING_DIMENSION
    for vec in vectors:
        if len(vec) != expected:
            raise ValueError(
                f"Embedding length {len(vec)} does not match JINA_EMBEDDING_DIMENSION={expected}; "
                "adjust the setting to match your JINA_EMBEDDINGS_MODEL output, and align app/schema.sql vector(N)."
            )
    return vectors


async def embed_texts_async(texts: list[str], *, task: str | None = None) -> list[list[float]]:
    """Async wrapper so kb_search does not block the event loop on HTTP I/O."""
    return await asyncio.to_thread(partial(embed_texts_sync, texts, task=task))
