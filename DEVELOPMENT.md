# DataCopilot - Development Guide

> Maintenance, security, and troubleshooting reference.

## Project Structure

```
DataCopilot/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Pydantic settings (v2)
│   ├── database.py         # Unified DB engine (sync + async)
│   ├── db.py               # Legacy DB module (imports from database.py)
│   ├── embeddings.py       # KB chunking & pgvector loading
│   ├── jina_client.py      # Jina Embeddings API client
│   ├── mcp_tools.py       # MCP tool implementations
│   ├── mock_data.py       # Mock data generation
│   ├── pii_masking.py     # PII protection
│   ├── schema.sql         # Database schema + indexes + FK constraints
│   ├── routes/
│   │   ├── ask.py        # POST /ask endpoint
│   │   └── tools.py      # Tool list & call endpoints
│   ├── static/
│   │   ├── index.html    # Vue 3 frontend shell
│   │   ├── css/style.css # Custom styles (dark mode, animations)
│   │   └── js/app.js     # Vue 3 composition API logic
│   └── kb_docs/          # Knowledge base markdown files
├── dbt/
│   ├── models/            # dbt transformations
│   └── tests/             # Data quality tests
├── docker-compose.yml    # Container orchestration
├── Dockerfile           # App container image
├── requirements.txt     # Python dependencies
├── PLAN.md              # Implementation plan
├── TODO.md              # Task tracking
└── README.md            # Project overview
```

---

## Security Features

1. **Read-only database access** — Only SELECT/WITH queries allowed
2. **PII masking** — Emails & names automatically masked in results
3. **Parameterized queries** — SQL injection protection
4. **Rate limiting** — 10 requests per minute on `/ask`
5. **Tool call logging** — All actions tracked
6. **Config validation** — Required API keys checked at startup

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
2. Rebuild: `docker-compose up --build -d`

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
   docker-compose exec app python -c "from app.embeddings import load_kb_documents; load_kb_documents()"
   ```

### Environment Variables

Edit `.env` and restart (no rebuild needed for env changes):
```bash
docker-compose down
docker-compose up -d
```

---

## Troubleshooting

### Database connection issues
```bash
docker-compose ps           # Check status
docker-compose restart db   # Restart database
```

### Missing API keys
Edit `.env` and restart:
```bash
docker-compose down
docker-compose up --build
```

### Rate limiting
Wait 60 seconds between requests, or adjust in `app/routes/ask.py`:
```python
_RATE_LIMIT_WINDOW_SECONDS = 60
_RATE_LIMIT_MAX_REQUESTS = 10
```
