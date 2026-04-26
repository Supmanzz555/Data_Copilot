#!/usr/bin/env python3
"""
Offline unit tests for recent plan implementations.
These tests do not require Docker or a running database.
"""
import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

# Ensure imports succeed in local/offline test mode
os.environ.setdefault("DATABASE_URL", "postgresql://admin:admin@localhost:5432/deep_insights")
os.environ.setdefault("GROQ_API_KEY", "test-key")
os.environ.setdefault("JINA_API_KEY", "test-key")

from app.database import _to_async_url
from app.routes import ask


class _MockCompletion:
    def __init__(self, content: str):
        self.choices = [SimpleNamespace(message=SimpleNamespace(content=content))]


class TestPlanUpdatesOffline(unittest.IsolatedAsyncioTestCase):
    def test_to_async_url_conversion(self):
        self.assertEqual(
            _to_async_url("postgresql://u:p@localhost:5432/db"),
            "postgresql+asyncpg://u:p@localhost:5432/db",
        )
        self.assertEqual(
            _to_async_url("postgresql+asyncpg://u:p@localhost:5432/db"),
            "postgresql+asyncpg://u:p@localhost:5432/db",
        )

    def test_schema_contains_indexes_and_cascade_fks(self):
        with open("app/schema.sql", "r", encoding="utf-8") as f:
            schema = f.read()

        self.assertIn("ON DELETE CASCADE", schema)
        self.assertIn("CREATE INDEX IF NOT EXISTS idx_tickets_customer_id", schema)
        self.assertIn("CREATE INDEX IF NOT EXISTS idx_logins_customer_id", schema)
        self.assertIn("CREATE INDEX IF NOT EXISTS idx_customer_products_customer_id", schema)
        self.assertIn("USING ivfflat (embedding vector_cosine_ops)", schema)

    async def test_rate_limit_on_ask_endpoint(self):
        async def fake_llm_decision(**kwargs):
            return _MockCompletion(json.dumps({"action": "chat", "response": "ok"}))

        ask._request_log.clear()
        payload = ask.AskPayload(question="hello")
        request = SimpleNamespace(client=SimpleNamespace(host="127.0.0.1"))

        with patch("app.routes.ask._groq_chat_create_with_backoff", fake_llm_decision):
            for _ in range(ask._RATE_LIMIT_MAX_REQUESTS):
                resp = await ask.ask_question(payload, request)
                self.assertEqual(resp.get("tool_used"), "conversational")

            blocked = await ask.ask_question(payload, request)
            self.assertEqual(blocked.get("error"), "rate_limit_exceeded")

        ask._request_log.clear()


if __name__ == "__main__":
    unittest.main()
