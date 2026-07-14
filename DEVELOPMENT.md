# DataCopilot - Development Guide

> Maintenance, security, and troubleshooting reference.

## Project Structure

```
DataCopilot/
├── app/
│   ├── __init__.py          # Package marker
│   ├── main.py              # FastAPI entry point (+ /health endpoint)
│   ├── config.py            # Pydantic settings (v2)
│   ├── database.py         # Unified DB engine (sync + async)
│   ├── embeddings.py       # KB chunking & pgvector loading
│   ├── guardrails.py       # Shared SQL guardrail (is_read_query)
│   ├── jina_client.py      # Jina Embeddings API client (reused httpx.Client)
│   ├── metrics.py          # Prometheus metrics (/metrics endpoint)
│   ├── mcp_tools.py       # MCP tool implementations (lazy pooled engine)
│   ├── mock_data.py       # Mock data generation
│   ├── pii_masking.py     # PII protection (email, name, phone)
│   ├── schema.sql         # Database schema + indexes + FK constraints
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── ask.py        # POST /ask endpoint (+ request logging, metrics)
│   │   └── tools.py      # Tool list & call endpoints
│   ├── static/
│   │   ├── index.html    # Vue 3 frontend shell
│   │   ├── css/style.css # Custom styles (dark mode, animations)
│   │   └── js/app.js     # Vue 3 composition API logic
│   └── kb_docs/          # Knowledge base markdown files
├── dbt/                  # dbt transformations (build separately)
├── grafana/              # Grafana provisioning (datasource + dashboard)
├── .dockerignore         # Excludes .git, __pycache__, .env from Docker context
├── .github/workflows/    # CI pipeline (test, security, docker)
├── docker compose.yml    # Container orchestration (profiles for monitoring)
├── Dockerfile           # App container image (non-root app user)
├── prometheus.yml       # Prometheus scrape config
├── requirements.txt     # Python dependencies (version-pinned)
├── test_mlops.py        # 28 MLOps integration tests
├── PLAN.md              # Implementation plan
├── TODO.md              # Task tracking
└── README.md            # Project overview
```

---

## Security Features

1. **Read-only database access** — Only single SELECT/WITH queries allowed (shared `app/guardrails.py`, sqlparse-enforced)
2. **PII masking** — Emails, names, and phone numbers automatically masked in results (fully masked)
3. **Parameterized queries** — SQL injection protection
4. **Rate limiting** — 10 requests per minute on `/ask` (returns HTTP 429)
5. **CORS middleware** — Configured for cross-origin access (local dev: allow all origins)
6. **Config validation** — Required API keys checked at startup, fails fast
7. **Multi-statement guardrail** — `sqlparse` rejects anything beyond a single SELECT/WITH
8. **Container security** — Runs as non-root `app` user (uid 1000), no `--reload`, `.dockerignore`
9. **Non-cascading FKs** — All foreign keys use `ON DELETE SET NULL` (prevents accidental data loss)
10. **Dedicated /health endpoint** — Lightweight health check, no filesystem I/O

---

## Frontend

### Architecture
- `index.html` — Vue 3 shell with Tailwind CDN, `marked`, `highlight.js`
- `css/style.css` — Custom styles (scrollbar, animations, dark mode, highlight.js theme, `msg-shadow`, `input-glow`)
- `js/app.js` — Vue 3 Composition API (sendMessage, chat persistence, CSV export, edit/resend, sortable paginated tables, search, keyboard shortcuts, timestamps)

### CDN Dependencies
- Vue 3: https://unpkg.com/vue@3/dist/vue.global.prod.js
- Tailwind: https://cdn.tailwindcss.com
- marked: https://cdn.jsdelivr.net/npm/marked/marked.min.js
- highlight.js 11.9.0: https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js

### Modifying
1. Edit files under `app/static/`
2. Rebuild: `docker compose up --build -d`

---

## Maintenance

### Adding New MCP Tools

1. **Define function in `app/mcp_tools.py`:**
   ```python
   async def my_new_tool(params: dict):
       return result
   ```

2. **Register in `app/routes/ask.py`:**
   ```python
   TOOLS = {
       "my_new_tool": my_new_tool,
       ...
   }
   ```

### Adding Knowledge Base Documents

1. Add markdown files to `app/kb_docs/`
2. Rebuild embeddings:
   ```bash
   docker compose exec app python -c "from app.embeddings import load_kb_documents; load_kb_documents()"
   ```

### Environment Variables

Edit `.env` and restart (no rebuild needed for env changes):
```bash
docker compose down
docker compose up -d
```

---

## Troubleshooting

### Database connection issues
```bash
docker compose ps           # Check status
docker compose restart db   # Restart database
```

### Missing API keys
Edit `.env` and restart:
```bash
docker compose down
docker compose up --build
```

### Rate limiting
Wait 60 seconds between requests, or adjust in `app/routes/ask.py`:
```python
_RATE_LIMIT_WINDOW_SECONDS = 60
_RATE_LIMIT_MAX_REQUESTS = 10
```

---

## Quick Reference

### Start Project
```bash
# Core only (app + db):
docker compose up --build

# Full stack (app + db + Prometheus + Grafana + Uptime Kuma):
docker compose --profile monitoring up --build
```

### Run Tests
```bash
bank/bin/python -m pytest test_plan_updates_unit.py test_frontend.py test_sql_guardrails.py -v
python test_mlops.py  # requires running app
```

### Key Files
| File | Purpose |
|------|---------|
| `app/main.py` | Entry point (+ /health, CORS, metrics) |
| `app/guardrails.py` | Shared SQL guardrail |
| `app/metrics.py` | Prometheus `/metrics` endpoint |
| `app/routes/ask.py` | Chat API with rate limit, logging, metrics |
| `app/schema.sql` | DB schema (SET NULL FKs, request_logs) |
| `app/mcp_tools.py` | Tool implementations (pooled engine) |
| `app/pii_masking.py` | PII masking (email, name, phone) |
| `test_mlops.py` | 28 MLOps integration tests |
| `docker-compose.yml` | Profiles: `monitoring` for full stack |
| `.github/workflows/ci.yml` | CI: test + security + docker |
