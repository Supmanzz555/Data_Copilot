# Plan: DataCopilot Improvements

## Goal
Fix the highest-impact reliability, performance, and security issues with a safe rollout order.

---

## Tasks

### 1. Add Database Indexes
**Priority**: HIGH

Add to `app/schema.sql`:

```sql
-- Indexes for tickets table
CREATE INDEX idx_tickets_customer_id ON tickets(customer_id);
CREATE INDEX idx_tickets_product_id ON tickets(product_id);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_created_at ON tickets(created_at);
CREATE INDEX idx_tickets_app_version ON tickets(app_version);

-- Indexes for logins table
CREATE INDEX idx_logins_customer_id ON logins(customer_id);

-- Indexes for customer_products table
CREATE INDEX idx_customer_products_customer_id ON customer_products(customer_id);
CREATE INDEX idx_customer_products_product_id ON customer_products(product_id);
CREATE INDEX idx_customer_products_status ON customer_products(status);

-- Indexes for kb_embeddings (vector search)
CREATE INDEX idx_kb_embeddings_embedding ON kb_embeddings USING ivfflat (embedding vector_cosine_ops);
```

---

### 2. Config Validation for Required API Keys
**Priority**: HIGH

Add startup/config validation so app fails fast with a clear message when required keys are missing.

Implementation guidance:
- Keep current Pydantic v1 style for now.
- Validate both `GROQ_API_KEY` and `JINA_API_KEY`.
- Prefer startup/runtime validation if you want clearer operational errors.

---

### 3. SQL Generation Reliability Hardening
**Priority**: HIGH

Improve NL->SQL robustness in `app/routes/ask.py`:
- Strengthen schema prompt constraints (exact table/column names and join keys).
- Keep and extend sanitizer for known bad patterns (alias mismatch, invalid group-by aliasing, hallucinated columns).
- Return friendly errors for malformed SQL.
- Add tests for common query intents and known failure cases.

---

### 4. Foreign Key Policy Cleanup (No Duplicate Constraints)
**Priority**: MEDIUM

`app/schema.sql` already defines foreign keys inline (`REFERENCES ...`).
Do NOT add duplicate `ALTER TABLE ... ADD CONSTRAINT` for the same relationships.

If cascade delete is desired, update existing FK definitions in table creation, for example:

```sql
customer_id INT REFERENCES customers(id) ON DELETE CASCADE
```

---

### 5. Unified Database Engine Module (Optional Refactor)
**Priority**: MEDIUM

Only do this after Tasks 1-4 are stable.
Unify sync/async engine creation in one module to reduce duplication.

Potential target:
- `app/database.py` containing sync and async engine/session factories.
- Consume from `app/db.py`, `app/mcp_tools.py`, `app/embeddings.py`, `app/mock_data.py`.

---

### 6. Embedding Path Validation and Fallback Quality
**Priority**: MEDIUM

Prefer simple, reliable checks over regex on stringified vectors:
- Enforce vector length equals `JINA_EMBEDDING_DIMENSION`.
- Handle Jina API and vector-cast failures cleanly.
- Keep text-search fallback path healthy and observable.

---

### 7. Remove Hardcoded Credentials
**Priority**: LOW

In `app/config.py`, defaults should come from `.env` only where practical.

Update `docker-compose.yml`:

```yaml
services:
  db:
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-admin}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-admin}
      POSTGRES_DB: ${POSTGRES_DB:-deep_insights}
```

---

### 8. Add Health Check for App in docker-compose
**Priority**: LOW

Update `docker-compose.yml`:

```yaml
services:
  app:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

---

### 9. dbt Execution Strategy
**Priority**: LOW

Avoid running dbt automatically on API startup.

Preferred approach:
- Run dbt in CI/CD or a separate one-shot job/container.
- Keep app boot fast and independent of dbt runtime failures.

---

### 10. Add Rate Limiting on /ask Endpoint
**Priority**: LOW

Add request limiting for basic abuse protection.

---

### 11. Production Logging Defaults
**Priority**: LOW

Keep debug SQL logging disabled by default in production.
Enable only when explicitly requested via env/config.

---

### 12. Upgrade to Pydantic v2
**Priority**: LOW

Treat as a separate migration milestone with dedicated compatibility tests.
Do not combine with reliability hotfix tasks.

---

## Execution Order
1. Task 1 (Indexes)
2. Task 2 (Config validation)
3. Task 3 (SQL generation reliability)
4. Task 4 (FK policy cleanup without duplicates)
5. Task 5 (Optional unified DB refactor)
6. Task 6 (Embedding-path validation and fallback quality)
7. Tasks 7-12 (low-priority hardening and maintenance)
