# TODO: dBank_Copilot - Implementation Tasks

## ✅ Completed Tasks

### Backend Improvements
- [x] Add database indexes on frequently queried columns
- [x] Add config validation for required API keys
- [x] Harden SQL generation reliability
- [x] Update FK delete behavior with ON DELETE CASCADE
- [x] DB engine unification (sync + async)
- [x] Improve embedding-path validation
- [x] Remove hardcoded credentials defaults
- [x] Add app health check in docker-compose
- [x] Keep debug SQL logging disabled by default
- [x] Upgrade to Pydantic v2

### Frontend
- [x] Vue 3 responsive frontend with dark mode
- [x] Modern minimal UI design
- [x] Message animations
- [x] Mobile responsive design

### Security & Performance
- [x] Rate limiting on /ask endpoint (10/min)
- [x] Connection pooling with pool_size, max_overflow
- [x] Query timeout (30 seconds)
- [x] Configurable similarity threshold
- [x] SQL sanitization

### Documentation
- [x] README.md - Complete project overview
- [x] DEVELOPMENT.md - Development guide
- [x] note.md - Quick summary
- [x] MLOPS_PLAN.md - MLOps implementation plan

---

## 📋 MLOps Implementation Plan (Pending)

See [MLOPS_PLAN.md](./MLOPS_PLAN.md) for detailed implementation steps.

### Phase 1: Observability
- [ ] Add `/metrics` endpoint with Prometheus client
- [ ] Create `app/metrics.py` with metric definitions
- [ ] Update `app/main.py` to include metrics router

### Phase 2: Monitoring Stack
- [ ] Update `docker-compose.yml` with monitoring services
  - [ ] prometheus (metrics collection)
  - [ ] grafana (dashboards)
  - [ ] uptime-kuma (external monitoring)
- [ ] Create `prometheus.yml` config
- [ ] Add `request_logs` table to `schema.sql`

### Phase 3: Dashboards & Alerts
- [ ] Setup Grafana dashboards
- [ ] Configure alert rules
- [ ] Setup Uptime Kuma

### Phase 4: CI/CD
- [ ] Create `.github/workflows/ci.yml`
- [ ] Add security scanning (bandit, safety)
- [ ] Add Docker build step

---

## Quick Reference

### Start Project
```bash
docker-compose up --build
```

### Run Tests
```bash
source bank/bin/activate
pytest test_plan_updates_unit.py -v
```

### Key Files
| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI entry point |
| `app/metrics.py` | Metrics (to be created) |
| `app/routes/ask.py` | Question answering |
| `docker-compose.yml` | Container orchestration |
| `MLOPS_PLAN.md` | MLOps implementation guide |

---

*Last updated: April 2026*