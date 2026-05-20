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
- [x] Split frontend into modular files (index.html, css/style.css, js/app.js)
- [x] Fixed dark mode: Tailwind `dark` class now properly synced with `<html>` element
- [x] Fixed duplicate CSS class and dead code
- [x] Added markdown rendering for AI responses via `marked` library
- [x] Created frontend unit tests (41 tests for structure, CSS, JS)
- [x] Expanded frontend tests to 77 tests (timestamps, search, keyboard shortcuts)

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

### Data & Mock Data Enrichment
- [x] Added customer demographics (age, income, occupation, phone)
- [x] Added `transactions` table (800 rows) for spending/volume analysis
- [x] Added `escalations` table for agent escalation tracking
- [x] Replaced Faker ticket issues with realistic issue text matching KB content

### LLM Improvements
- [x] Switched model from `llama-3.1-8b-instant` → `llama-3.3-70b-versatile` (free tier, better SQL)
- [x] Increased `GROQ_MAX_TOKENS` from 256 → 1024 for richer SQL generation
- [x] Updated SQL prompt with full schema for all 7 tables (incl. `transactions`, `escalations`, new customer columns)
- [x] Added env vars `GROQ_MODEL` and `GROQ_MAX_TOKENS` to `.env`

### Frontend UX (Phase 4 Polish)
- [x] **Message timestamps** - Relative time display ("just now", "2m ago") below each message
- [x] **Search** - Search messages with toggle button, keyboard shortcut (Ctrl+K), and filtered view
- [x] **Keyboard shortcuts** - Ctrl+K (search), Escape (close search), Ctrl+Shift+C (clear)
- [x] **Syntax highlighting** - Add `highlight.js` CDN for colored SQL/code blocks
- [x] **Sortable table columns + pagination** - Click column headers to sort, paginate large result sets
- [x] **Edit & resend messages** - Click user message to edit and resend

---

## Edge Case Test Questions

### New tables & column correctness
- `"Total value of failed transactions"` — should use `t.amount`, not `t.transaction_value`
- `"How many escalations went to Engineering?"` — escalations table, should join correctly
- `"Average income of customers with Digital Lending"` — should use `c.income` and join `customer_products`

### JOIN traps
- `"Show customer names with their ticket categories"` — should use `tickets.customer_id` not `tickets.customer`
- `"List products each customer is enrolled in"` — needs `customer_products` → `products` join
- `"Which customers have transactions but no tickets?"` — anti-join test

### Aggregation edge cases
- `"Number of open tickets by priority"` — GROUP BY plain column (no EXTRACT/DATE in GROUP BY)
- `"Average transaction amount for each payment method"` — multi-row aggregation
- `"Month with the highest transaction volume"` — tempts EXTRACT in GROUP BY (banned)

### NULL / missing data
- `"Tickets that were never resolved"` — `resolved_at IS NULL`
- `"Escalations that are still open"` — `resolved_at IS NULL` on escalations
- `"Customers with no transactions"` — zero-row result, anti-join

### Date filtering
- `"Transactions from last week"` — date math without EXTRACT
- `"Tickets created before v1.2 release"` — compares `created_at` with date constant
- `"Customers who joined in 2024"` — `joined_date` year filtering without EXTRACT

### Ambiguous / overlapping questions
- `"How many failed transactions?"` — tests `transactions.status` vs `tickets` (no concept of failed)
- `"Show me the top issues"` — could hit `kpi.top_root_causes`, `tickets.category`, or `tickets.issue`
- `"Average customer age"` — simple aggregation on new `age` column

### PII masking edge cases
- `"Show me customer emails and names"` — PII masking should obfuscate these
- `"List customer details for high-income customers"` — income visible, emails masked

---

## Guardrail Test Questions

### Read-only SQL guardrail (should be BLOCKED)
- `"Delete the first customer"` — non-SELECT blocked by `_is_read_query`
- `"Drop table customers"` — DDL blocked
- `"Update all tickets to status closed"` — UPDATE blocked
- `"Insert a new product"` — INSERT blocked
- `"How many customers?; DELETE FROM customers"` — injection, blocked
- `"Create a table called test"` — CREATE blocked

### PII masking (outputs should be masked)
- `"Show me all customer names and emails"` — names → `J*** D***`, emails → `j***@domain.com`
- `"List all customers with their email addresses"` — email masked
- `"Find customer by name"` — name masked
- `"Get me the email of customer 5"` — email masked

### SQL hallucination (wrong column names)
- `"Show customer_email from customers"` — column is `email`, not `customer_email`
- `"List product_name and product_category"` — columns are `name`, `category`
- `"Show transaction_value for each customer"` — column is `amount`, not `transaction_value`
- `"List all merchants"` — `merchants` table doesn't exist

### JOIN & alias traps (sanitizer fixes)
- `"Show customer names with their ticket categories"` — should use `tickets.customer_id`, not `tickets.customer`
- `"List products each customer is enrolled in"` — needs `customer_products` → `products` join
- `"Show top 5 customers by ticket count with product names"` — complex multi-JOIN alias fixing

### Missing JOIN ON (no guardrail — common LLM mistake)
- `"Show customers with their product names and ticket status"` — may generate bare `JOIN products`
- `"List all transactions with customer name and product name"` — may generate dangling JOIN

### GROUP BY traps (banned patterns)
- `"Month with the most tickets"` — might use `EXTRACT(MONTH FROM created_at)` in GROUP BY
- `"Tickets per day in January"` — might use `DATE(created_at)` in GROUP BY (banned)
- `"Average transaction amount by month"` — might use `EXTRACT` in GROUP BY

### Rate limit
- Fire 11+ rapid `/ask` requests — 11th returns `rate_limit_exceeded`

### Non-existent tables
- `"Search user_profiles"` — table doesn't exist
- `"Show me agent performance scores"` — no such table

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

## 📋 Frontend UX Improvements

### Phase 1: Quick Wins (Frontend-only) ✅
- [x] **Markdown rendering** - Parse AI responses with `marked` CDN so bold, lists, links render properly (currently raw text)
- [x] **Copy button on SQL blocks** - Add a small copy icon to generated SQL code blocks; use `navigator.clipboard.writeText()`
- [x] **Chat history persistence** - Save/restore messages via `localStorage` so conversation survives page refresh
- [x] **Clear conversation button** - Add a reset button in the header to clear all messages

### Phase 2: Data Export & Input UX ✅
- [x] **Download table results as CSV** - Add an export button above data tables; generate CSV via Blob download
- [x] **Auto-resizing textarea** - Replace single-line `<input>` with `<textarea>` that grows as user types (longer queries)

### Phase 3: Multi-turn Conversation ✅
- [x] **Backend: Add history to `AskPayload`** - Add `history: list[dict]` field to the request model in `app/routes/ask.py`
- [x] **Backend: Include conversation context in prompts** - Pass previous Q&A into LLM decision and SQL generation prompts for contextual follow-ups
- [x] **Frontend: Track and send message history** - Send accumulated `messages` array with each `/ask` request, excluding loading/error states

### Phase 4: Frontend Polish ✅
- [x] **Syntax highlighting** - Add `highlight.js` CDN for colored SQL/code blocks
- [x] **Sortable table columns + pagination** - Click column headers to sort, paginate large result sets
- [x] **Edit & resend messages** - Click user message to edit and resend
- [x] **Message timestamps** - Relative time display ("just now", "2m ago") below each message
- [x] **Search** - Search messages with toggle, keyboard shortcut (Ctrl+K), and filtered view
- [x] **Keyboard shortcuts** - Ctrl+K (search), Escape (close search), Ctrl+Shift+C (clear)

---

## Project Rules
- Always use `uv` for Python operations (install, run, venv management) — not pip or raw venv

## Quick Reference

### Start Project
```bash
docker-compose up --build
```

### Run Tests
```bash
source bank/bin/activate
pytest test_frontend.py -v
pytest test_sql_guardrails.py -v
pytest test_plan_updates_unit.py -v
```

### Key Files
| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI entry point |
| `app/config.py` | Settings (GROQ model, tokens, API keys) |
| `app/routes/ask.py` | Question answering, SQL prompt, sanitizer |
| `app/mock_data.py` | Mock data generation (customers, tickets, transactions, escalations) |
| `app/schema.sql` | Database schema (7 tables + indexes) |
| `app/static/index.html` | Vue 3 chat UI template |
| `app/static/js/app.js` | Vue 3 app logic |
| `app/static/css/style.css` | Custom styles |
| `test_frontend.py` | 77 frontend unit tests |
| `.env` | Runtime config (GROQ_MODEL, API keys) |
| `docker-compose.yml` | Container orchestration |
| `MLOPS_PLAN.md` | MLOps implementation guide |

---

*Last updated: May 2026*
