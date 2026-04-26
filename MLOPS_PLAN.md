# dBank_Copilot - Complete Project Plan

## Part 1: Current Project Overview

An AI-powered support system for dBank's Operations team that answers natural-language questions grounded in company data, executes safe SQL queries, and provides knowledge base search.

### Tech Stack
| Layer | Technology |
|-------|------------|
| Backend | FastAPI + Python |
| Database | PostgreSQL 18 + pgvector |
| LLM | Groq |
| Embeddings | Jina AI |
| Frontend | Vue 3 + Tailwind CSS |
| Container | Docker |

### Project Structure
```
dBank_Copilot/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py           # Pydantic settings
│   ├── database.py         # SQLAlchemy engines with pooling
│   ├── embeddings.py       # KB chunking & loading
│   ├── jina_client.py     # Jina Embeddings API client
│   ├── mcp_tools.py        # MCP tool implementations
│   ├── mock_data.py        # Mock data generation
│   ├── pii_masking.py       # PII protection
│   ├── schema.sql          # DB schema + indexes
│   ├── routes/
│   │   ├── ask.py          # POST /ask endpoint
│   │   └── tools.py        # Tool endpoints
│   ├── static/
│   │   └── index.html     # Vue 3 responsive frontend
│   └── kb_docs/            # Knowledge base markdown files
├── dbt/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── bank/                   # uv virtual environment
```

---

## Part 2: MLOps Plan - Separated Containers Architecture

### Architecture Diagram
```
┌─────────────────────────────────────────────────────────────────────┐
│                      dBank_Copilot Stack                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐        │
│  │    App     │───→│ PostgreSQL │◄───│  Prometheus      │        │
│  │  (FastAPI) │    │   + pgvec   │    │  (scrape metrics)│        │
│  │   :8000    │    │    :5432    │    │   :9090         │        │
│  └─────────────┘    └─────────────┘    └───────┬─────────┘        │
│                                                  │                │
│                                                  ▼                │
│  ┌─────────────┐    ┌─────────────────────────────────────┐        │
│  │ Uptime Kuma│◄───│           Grafana                     │        │
│  │ (monitor)  │    │  Dashboards / Alerting    :3000       │        │
│  │  :3001     │    └─────────────────────────────────────┘        │
│  └─────────────┘                                                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Containers to Add

| Container | Image | Port | Purpose |
|------------|-------|------|---------|
| `db` | pgvector/pgvector:pg18-trixie | 5432 | Database |
| `app` | Built from Dockerfile | 8000 | FastAPI application |
| `prometheus` | prom/prometheus:latest | 9090 | Metrics collection |
| `grafana` | grafana/grafana:latest | 3000 | Dashboards & Alerting |
| `uptime-kuma` | louis711/uptime-kuma:latest | 3001 | External uptime monitoring |

---

## Part 3: Implementation Steps

### Step 1: Add Prometheus Metrics Endpoint

Create `app/metrics.py`:
```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import APIRouter, Response

router = APIRouter()

# Metrics
REQUEST_COUNT = Counter('dbank_requests_total', 'Total requests', ['tool'])
REQUEST_LATENCY = Histogram('dbank_request_latency_seconds', 'Request latency', ['tool'])
ACTIVE_REQUESTS = Gauge('dbank_active_requests', 'Active requests')
ERROR_COUNT = Counter('dbank_errors_total', 'Total errors', ['type'])

@router.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type="text/plain")
```

### Step 2: Update docker-compose.yml

Add these services to existing docker-compose.yml:
```yaml
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    depends_on:
      - app

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD:-admin}
      GF_USERS_ALLOW_SIGN_UP: "false"
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus

  uptime-kuma:
    image: louis711/uptime-kuma:latest
    ports:
      - "3001:3001"
    volumes:
      - uptime_kuma_data:/app/data
    restart: unless-stopped

volumes:
  grafana_data:
  uptime_kuma_data:
```

### Step 3: Create prometheus.yml

Create `prometheus.yml`:
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'dBank_Copilot'
    static_configs:
      - targets: ['app:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

### Step 4: Add Request Logging to Schema

Add to `app/schema.sql`:
```sql
CREATE TABLE request_logs (
    id SERIAL PRIMARY KEY,
    question TEXT,
    tool_used TEXT,
    latency_ms INT,
    success BOOLEAN,
    error TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_request_logs_created ON request_logs(created_at);
```

### Step 5: Update requirements.txt

Add these packages:
```
prometheus-client>=0.17.0
```

---

## Part 4: Monitoring Metrics to Track

### App Metrics (from /metrics endpoint)
| Metric | Type | Purpose |
|--------|------|---------|
| `dbank_requests_total` | Counter | Total requests by tool |
| `dbank_request_latency_seconds` | Histogram | Request latency distribution |
| `dbank_active_requests` | Gauge | Currently active requests |
| `dbank_errors_total` | Counter | Errors by type |

### Database Metrics
| Metric | Type | Purpose |
|--------|------|---------|
| Query latency | Histogram | Database query times |
| Connection pool usage | Gauge | Active connections |

### System Metrics
| Metric | Type | Purpose |
|--------|------|---------|
| CPU/Memory | Gauge | Container resource usage |
| Health check status | Binary | Service availability |

---

## Part 5: Alert Rules

| Alert | Condition | Action |
|-------|-----------|--------|
| High Error Rate | error_rate > 5% in 5m | Slack/Email |
| High Latency | p95_latency > 5s | Slack/Email |
| Service Down | healthcheck fails | Uptime Kuma alert |
| DB Connection Full | pool_usage > 90% | Slack/Email |

---

## Part 6: Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `app/metrics.py` | Create | Prometheus metrics definitions |
| `app/main.py` | Modify | Add `/metrics` route |
| `app/routes/ask.py` | Modify | Add request logging |
| `app/schema.sql` | Modify | Add `request_logs` table |
| `docker-compose.yml` | Modify | Add monitoring services |
| `prometheus.yml` | Create | Prometheus configuration |
| `requirements.txt` | Modify | Add prometheus-client |
| `.github/workflows/ci.yml` | Create | GitHub Actions CI/CD |

---

## Part 7: Testing the Stack

```bash
# Start all services
docker-compose up --build

# Check metrics
curl http://localhost:9090/metrics

# Check app metrics
curl http://localhost:8000/metrics

# Access services
# - App: http://localhost:8000
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3000 (admin/admin)
# - Uptime Kuma: http://localhost:3001
```

---

## Part 8: CI/CD Pipeline

Create `.github/workflows/ci.yml`:
```yaml
name: CI

on:
  push:
    branches: [main, indev]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run tests
        run: pytest test_plan_updates_unit.py -v

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Security scan
        run: |
          pip install bandit safety
          bandit -r app/
          safety check

  docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker
        run: docker-compose build app
```

---

## Part 9: Implementation Order

| Order | Task | Effort | Impact |
|-------|------|--------|--------|
| 1 | Add `/metrics` endpoint | Low | High |
| 2 | Update `docker-compose.yml` | Low | High |
| 3 | Create `prometheus.yml` | Low | Medium |
| 4 | Setup Grafana dashboards | Medium | High |
| 5 | Add request logging to DB | Medium | High |
| 6 | Setup Uptime Kuma | Low | Medium |
| 7 | Configure alerts | Medium | High |
| 8 | Create CI/CD pipeline | High | High |

---

## Summary Checklist

- [ ] Add `/metrics` endpoint with Prometheus client
- [ ] Update `docker-compose.yml` with 3 new services (prometheus, grafana, uptime-kuma)
- [ ] Create `prometheus.yml` config
- [ ] Add `app/metrics.py` with metric definitions
- [ ] Update `app/main.py` to include metrics router
- [ ] Add `request_logs` table to `schema.sql`
- [ ] Update `requirements.txt` with prometheus-client
- [ ] Setup Grafana dashboards
- [ ] Setup Uptime Kuma for external monitoring
- [ ] Configure alert rules
- [ ] Create `.github/workflows/ci.yml`

---

*Last updated: April 2026*
*Ready for implementation by any agent or developer*
*See also: README.md, DEVELOPMENT.md, TODO.md*