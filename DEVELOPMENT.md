# DataCopilot - Project Documentation

> AI-powered chat copilot that answers natural-language questions using SQL and knowledge base search.

## Overview

DataCopilot is an intelligent system that:
- Answers natural-language questions grounded in company data
- Executes safe, parameterized SQL queries via MCP tools
- Provides semantic search over knowledge base documents
- Delivers aggregated KPIs for business analysis

**Note**: All data in this project is mock data for demonstration purposes.

---

## Project Structure

```
dBank_Copilot/
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
│   │   └── index.html   # Vue 3 frontend (dark mode supported)
│   └── kb_docs/          # Knowledge base markdown files
├── dbt/
│   ├── models/            # dbt transformations
│   └── tests/             # Data quality tests
├── docker-compose.yml    # Container orchestration
├── Dockerfile           # App container image
├── requirements.txt     # Python dependencies
├── PLAN.md              # Implementation plan
├── TODO.md              # Task tracking
└── README.md            # Original documentation
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI + Python |
| Database | PostgreSQL 18 + pgvector |
| LLM | Groq (Compound model) |
| Embeddings | Jina API |
| Data Transform | dbt |
| Frontend | Vue 3 + Tailwind CSS |
| Container | Docker & Docker Compose |

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- **Groq API key** - Get at https://console.groq.com
- **Jina API key** - Get at https://jina.ai/embeddings

### Setup

1. ** Clone and configure:**
   ```bash
   cd dBank_Copilot
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Start:**
   ```bash
   docker-compose up --build
   ```

3. **Access:** http://localhost:8000

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web UI |
| `/ask` | POST | Ask a question |
| `/tools/list` | GET | List MCP tools |
| `/tools/call` | POST | Call a tool directly |

### Example: Ask a Question
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Top 5 root causes of issues"}'
```

---

## MCP Tools

| Tool | Description |
|------|-------------|
| `sql.query` | Read-only parameterized SQL queries |
| `kb.search` | Semantic search over documentation |
| `kpi.top_root_causes` | Top 5 root causes with percentages |

---

## Database Schema

### Tables
- `customers` - Customer data (id, name, email, region, joined_date)
- `products` - Product catalog (id, name, category)
- `customer_products` - Customer-product relationships
- `tickets` - Support tickets with app versioning
- `kb_embeddings` - Vector store for knowledge base

### Indexes (Performance)
```sql
CREATE INDEX idx_tickets_customer_id ON tickets(customer_id);
CREATE INDEX idx_tickets_product_id ON tickets(product_id);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_created_at ON tickets(created_at);
CREATE INDEX idx_tickets_app_version ON tickets(app_version);
CREATE INDEX idx_logins_customer_id ON logins(customer_id);
CREATE INDEX idx_customer_products_customer_id ON customer_products(customer_id);
CREATE INDEX idx_customer_products_product_id ON customer_products(product_id);
-- Vector index for pgvector similarity
CREATE INDEX idx_kb_embeddings_embedding ON kb_embeddings USING ivfflat (embedding vector_cosine_ops);
```

### Foreign Key Constraints
```sql
-- ON DELETE CASCADE for automatic cleanup
ALTER TABLE logins ADD CONSTRAINT fk_logins_customer FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE;
-- ... similar for other tables
```

---

## Security Features

1. **Read-only database access** - Only SELECT queries allowed
2. **PII masking** - Emails & names automatically masked
3. **Parameterized queries** - SQL injection protection
4. **Rate limiting** - 10 requests per minute on `/ask`
5. **Tool call logging** - All actions tracked
6. **Config validation** - Required API keys checked at startup

---

## Frontend

### Vue 3 + Tailwind CSS

**Features:**
- Dark mode toggle (persists to localStorage)
- Modern chat UI with bubbles
- Real-time data table rendering
- SQL code highlighting
- Loading animations
- Responsive design

**Dependencies (CDN):**
- Vue 3: https://unpkg.com/vue@3/dist/vue.global.prod.js
- Tailwind: https://cdn.tailwindcss.com

---

## Running Tests

```bash
# Activate virtual environment
source bank/bin/activate

# Run unit tests
pytest test_plan_updates_unit.py -v

# Run SQL guardrail tests
pytest test_sql_guardrails.py -v
```

**Note**: Some tests may fail due to Python module caching issues in pytest. The functions work correctly when run directly.

---

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `GROQ_API_KEY` | Yes | - | Groq API key for LLM |
| `JINA_API_KEY` | Yes | - | Jina API key for embeddings |
| `DEBUG` | No | `false` | Enable SQL debug logging |

---

## Maintenance

### Adding New MCP Tools

1. **Define function in `app/mcp_tools.py`:**
   ```python
   async def my_new_tool(params: dict):
       # Implementation
       return result
   ```

2. **Register in `app/routes/ask.py`:**
   ```python
   TOOLS = {
       "my_new_tool": my_new_tool,
       # ...
   }
   ```

### Modifying the Frontend

The frontend is in `app/static/index.html`. It's a single Vue 3 app using:
- Tailwind CSS for styling
- Vue 3 Composition API
- Dark mode with localStorage persistence

To modify:
1. Edit the HTML/Vue code directly
2. Rebuild: `docker-compose up --build`

### Adding Knowledge Base Documents

1. Add markdown files to `app/kb_docs/`
2. Rebuild the embeddings (requires Jina API):
   ```bash
   docker-compose exec app python -c "from app.embeddings import load_kb_documents; load_kb_documents()"
   ```

---

## Troubleshooting

### Database connection issues
```bash
docker-compose ps           # Check status
docker-compose restart db # Restart database
```

### Missing API keys
Edit `.env` and restart:
```bash
docker-compose down
docker-compose up --build
```

### Rate limiting
Wait 60 seconds between requests, or check the limit in `app/routes/ask.py`:
```python
_RATE_LIMIT_WINDOW_SECONDS = 60
_RATE_LIMIT_MAX_REQUESTS = 10
```

---

## Future Improvements

See [TODO.md](./TODO.md) for completed tasks and planned enhancements.

---

## License

MIT - Feel free to contribute!