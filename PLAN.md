# Plan: DataCopilot Improvements

## Goal
Fix the highest-impact reliability, performance, and security issues with a safe rollout order.

---

## Tasks

### 1. Add Database Indexes
**Priority**: HIGH — ✅ Done

Indexes added to `app/schema.sql` for tickets, logins, customer_products, transactions, escalations, and pgvector ivfflat.

---

### 2. Config Validation for Required API Keys
**Priority**: HIGH — ✅ Done

Startup validation in `app/main.py` checks `GROQ_API_KEY`, `JINA_API_KEY`, `DATABASE_URL` and fails fast with clear message.

---

### 3. SQL Generation Reliability Hardening
**Priority**: HIGH — ✅ Done

Enhanced schema prompts, alias-mismatch sanitizer, hallucinated-column fixes, friendly SQL error messages.

---

### 4. Foreign Key Policy (CASCADE → SET NULL)
**Priority**: HIGH — ✅ Done

All FK `ON DELETE CASCADE` changed to `ON DELETE SET NULL` in `app/schema.sql` to prevent accidental cascading deletes.

---

### 5. Multi-Statement SQL Guardrail
**Priority**: HIGH — ✅ Done

Added `sqlparse` library to verify single SELECT/WITH statements. Applied in both `app/routes/ask.py:_is_read_query` and `app/mcp_tools.py:_is_read_query` for defense-in-depth.

---

### 6. Rate Limit Returns HTTP 429
**Priority**: HIGH — ✅ Done

Rate-limited `/ask` requests now return HTTP 429 (was 200) with `JSONResponse`.

---

### 7. PII Masking — Phone Field
**Priority**: HIGH — ✅ Done

Added `mask_phone()` function and `"phone"`/`"customer_phone"` keys to `app/pii_masking.py`. Phone numbers are now masked in query results.

---

### 8. CORS Middleware
**Priority**: HIGH — ✅ Done

Added `CORSMiddleware` to `app/main.py` (allow all origins for local dev).

---

### 9. Docker Security Hardening
**Priority**: HIGH — ✅ Done

- Container runs as non-root `app` user (uid 1000)
- Removed `--reload` from `entrypoint.sh`
- Removed `dbt/`, `init_db.py`, `test_system.py` from Docker image
- Added `PYTHONDONTWRITEBYTECODE` and `PYTHONUNBUFFERED` env vars

---

### 10. Connection Pooling (Engine Reuse)
**Priority**: HIGH — ✅ Done

`app/mcp_tools.py` now lazy-initializes and reuses a single `AsyncEngine` instead of creating/disposing one per request.

---

### 11. Requirements Version Pinning
**Priority**: HIGH — ✅ Done

All dependencies pinned with `>=x,<y` ranges in `requirements.txt`. Added `sqlparse`. Removed `dbt-core` (unused at runtime, saves ~100MB in image).

---

### 12. Default Credentials
**Priority**: HIGH — ✅ Done

Default DB password changed from `admin` to `changeme` in `.env.example`.

---

### 13. CORS Fix
**Priority**: HIGH — ✅ Done

Removed `allow_credentials=True` (incompatible with `allow_origins=["*"]`).

---

### 14. Phone Masking Fix
**Priority**: HIGH — ✅ Done

`mask_phone` now fully masks (e.g. `081-***-****` instead of leaking last 4 digits).

---

### 15. Audit Log Visibility
**Priority**: HIGH — ✅ Done

`_log_request` failures now log a warning instead of silent `pass`. Removed 500-char truncation.

---

### 16. GROUP BY AS Alias Fix
**Priority**: HIGH — ✅ Done

Regex rewritten to handle multi-column GROUP BY clauses correctly without consuming trailing ORDER BY.

---

### 17. Schema Test Fix
**Priority**: HIGH — ✅ Done

Test asserts `ON DELETE SET NULL` (matches actual schema).

---

### 18. CI Coverage Expanded
**Priority**: MEDIUM — ✅ Done

CI now runs `test_plan_updates_unit.py`, `test_frontend.py`, and `test_sql_guardrails.py` (was 1 of 5).

---

### 19. Multi-Worker Uvicorn
**Priority**: MEDIUM — ✅ Done

Added `--workers 4` to uvicorn in `entrypoint.sh`.

---

### 20. Shared Guardrails Module
**Priority**: LOW — ✅ Done

Extracted `is_read_query` into `app/guardrails.py`, imported by both `ask.py` and `mcp_tools.py`.

---

### 21. Dead Code Removal
**Priority**: LOW — ✅ Done

Deleted unused `app/db.py`. Added `.dockerignore`.

---

### 22. Static Path Fix
**Priority**: LOW — ✅ Done

Static mount now uses `os.path.dirname(__file__)` instead of relative path.

---

### 23. HTTP Client Reuse
**Priority**: LOW — ✅ Done

Module-level `httpx.Client` in `jina_client.py` instead of per-call creation.

---

### 24. /health Endpoint
**Priority**: LOW — ✅ Done

Added lightweight `/health` endpoint. Docker healthcheck updated to use it.

---

### 25. db Engine Cleanup
**Priority**: LOW — ✅ Done

Removed unused async engine from `database.py`. `mcp_tools.py` owns the single pooled engine.

---

### 26. dbt Execution Strategy
**Priority**: LOW

Avoid running dbt automatically on API startup. Run dbt in CI/CD or a separate one-shot job/container.

---

### 27. Production Logging Defaults
**Priority**: LOW

Keep debug SQL logging disabled by default in production.

---

## Execution Order
1. ✅ Tasks 1-25 (Production hardening, MLOps, CI/CD)
2. ⬜ Tasks 26-27 (Low-priority maintenance)
