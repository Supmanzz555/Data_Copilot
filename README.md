# DataCopilot

AI chat copilot that turns natural language questions into SQL and knowledge-base lookups.

## Quick Start

```bash
cp .env.example .env   # add your Groq + Jina API keys
docker compose up --build
open http://localhost:8000
```

### Questions to try
- "How many customers do we have?"
- "Total transaction value by payment method"
- "Top 5 root causes of issues"
- "What is Digital Lending?"

## Tech Stack

| Layer | What |
|-------|------|
| Backend | FastAPI (Python 3.11) |
| Database | PostgreSQL 18 + pgvector |
| LLM | Groq (llama-3.3-70b-versatile) |
| Embeddings | Jina AI (jina-embeddings-v3) |
| Frontend | Vue 3 + Tailwind CSS |
| Container | Docker + Docker Compose |

## API

| Endpoint | What it does |
|----------|-------------|
| `GET /` | Chat UI |
| `POST /ask` | Ask a question in natural language |
| `GET /tools/list` | List available tools |
| `POST /tools/call` | Call a tool directly |
| `GET /metrics` | Prometheus metrics |
| `GET /health` | Health check |

## Run Modes

```bash
# Core only (app + db):
docker compose up --build

# Full stack (app + db + Prometheus + Grafana + Uptime Kuma):
docker compose --profile monitoring up --build
```

## Tests

```bash
bank/bin/python -m pytest test_plan_updates_unit.py test_frontend.py test_sql_guardrails.py -v
python test_mlops.py  # requires running app
```

## Project Structure

```
DataCopilot/
├── app/
│   ├── main.py              # Entry point (+ /health, CORS, metrics)
│   ├── config.py            # Pydantic settings
│   ├── database.py          # DB engines (connection pooling)
│   ├── embeddings.py        # KB chunking & pgvector loading
│   ├── guardrails.py        # Shared SQL guardrail
│   ├── jina_client.py       # Jina Embeddings client
│   ├── metrics.py           # Prometheus metrics
│   ├── mcp_tools.py         # Tool implementations
│   ├── mock_data.py         # Mock data generator
│   ├── pii_masking.py       # PII protection
│   ├── schema.sql           # Schema + indexes + FKs
│   ├── routes/
│   │   ├── ask.py           # POST /ask (rate limited, logged)
│   │   └── tools.py         # Tool endpoints
│   ├── static/              # Vue 3 frontend
│   └── kb_docs/             # Knowledge base files
├── grafana/                 # Provisioned dashboards
├── .github/workflows/ci.yml # CI pipeline
├── docker-compose.yml       # Profiles for monitoring stack
├── Dockerfile               # Non-root app user
├── prometheus.yml           # Scrape config
├── test_mlops.py            # 28 MLOps integration tests
└── requirements.txt         # Version-pinned deps
```

## Monitoring (MLOps)

| Service | URL | Purpose |
|---------|-----|---------|
| Prometheus | http://localhost:9090 | Metrics store |
| Grafana | http://localhost:3000 | Dashboards (admin/admin) |
| Uptime Kuma | http://localhost:3001 | Uptime monitoring |

Uses `docker compose --profile monitoring up -d` to start all.

## Database Tables

| Table | Purpose |
|-------|---------|
| `customers` | Customer data (name, email, region, age, income, phone) |
| `products` | Product catalog |
| `customer_products` | Customer-product enrollments |
| `logins` | Login history |
| `transactions` | Financial transactions |
| `tickets` | Support tickets with realistic issues |
| `escalations` | Ticket escalation tracking |
| `kb_embeddings` | Vector store (pgvector) |
| `request_logs` | Audit log of all /ask requests |

## Security

- Read-only SQL (single SELECT/WITH enforced by sqlparse)
- PII masking (email, name, phone)
- Rate limiting (10/min, HTTP 429)
- Multi-statement guardrail
- Non-root container user
- Config validation on startup

## CI/CD

GitHub Actions runs on push to `main`/`indev`:
- **test** — 3 test suites (82 tests)
- **security** — bandit + safety scan
- **docker** — verifies image builds

*Uses mock data for demonstration.*
