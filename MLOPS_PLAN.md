# DataCopilot - MLOps Plan

## Architecture

### Architecture Diagram
```
┌─────────────────────────────────────────────────────────────────────┐
│                         DataCopilot Stack                            │
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

## Implementation Steps

### Step 1: Add Prometheus Metrics Endpoint

Create `app/metrics.py`:
```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import APIRouter, Response

router = APIRouter()

# Metrics
REQUEST_COUNT = Counter('datacopilot_requests_total', 'Total requests', ['tool'])
REQUEST_LATENCY = Histogram('datacopilot_request_latency_seconds', 'Request latency', ['tool'])
ACTIVE_REQUESTS = Gauge('datacopilot_active_requests', 'Active requests')
ERROR_COUNT = Counter('datacopilot_errors_total', 'Total errors', ['type'])

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
  - job_name: 'DataCopilot'
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

## Monitoring Metrics to Track

### App Metrics (from /metrics endpoint)
| Metric | Type | Purpose |
|--------|------|---------|
| `datacopilot_requests_total` | Counter | Total requests by tool |
| `datacopilot_request_latency_seconds` | Histogram | Request latency distribution |
| `datacopilot_active_requests` | Gauge | Currently active requests |
| `datacopilot_errors_total` | Counter | Errors by type |

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

## Alert Rules

| Alert | Condition | Action |
|-------|-----------|--------|
| High Error Rate | error_rate > 5% in 5m | Slack/Email |
| High Latency | p95_latency > 5s | Slack/Email |
| Service Down | healthcheck fails | Uptime Kuma alert |
| DB Connection Full | pool_usage > 90% | Slack/Email |

---

## Files to Create/Modify

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

## Testing the Stack

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

## CI/CD Pipeline

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

## Implementation Order

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