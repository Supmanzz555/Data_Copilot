# Deep Insights Copilot (Data_Copilot)

> AI-powered support system for Operations team that answers natural-language questions grounded in company data.

## Overview

Deep Insights Copilot is an intelligent system that allows business users to query database and documentation using natural language, without writing SQL. It leverages LLM (Groq) for natural language understanding and PostgreSQL + pgvector for data storage and semantic search.

**Note**: This project uses mock data for demonstration purposes.

---

## Features

### Core Features
- **Natural Language to SQL** - Convert plain English questions into executable SQL queries
- **Knowledge Base Search** - Semantic search over documentation using embeddings
- **KPI Analytics** - Pre-built queries for common metrics (top root causes, etc.)
- **Rate Limiting** - 10 requests per minute to prevent abuse

### Security Features
- **Read-only Database** - Only SELECT/WITH queries allowed
- **PII Masking** - Automatically masks emails and customer names
- **SQL Sanitization** - Fixes common LLM-generated SQL mistakes
- **Request Validation** - Config validation at startup

### UI Features
- **Modern Vue 3 Interface** - Clean, responsive chat UI
- **Dark Mode** - Toggle between light and dark themes
- **Data Visualization** - Results displayed in formatted tables
- **SQL Preview** - Shows generated SQL before execution
- **Animations** - Smooth message animations and loading states

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Backend** | FastAPI + Python | REST API server |
| **Database** | PostgreSQL 18 + pgvector | Relational DB + vector store |
| **LLM** | Groq (llama-3.1-8b-instant) | Natural language understanding |
| **Embeddings** | Jina AI (jina-embeddings-v3) | Document vectorization |
| **Frontend** | Vue 3 + Tailwind CSS | Responsive chat interface |
| **Container** | Docker + Docker Compose | Deployment |

---

## Project Structure

```
dBank_Copilot/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py           # Pydantic settings (API keys, config)
│   ├── database.py         # SQLAlchemy engines with connection pooling
│   ├── db.py               # Legacy DB module (imports from database.py)
│   ├── embeddings.py       # Knowledge base chunking & loading
│   ├── jina_client.py      # Jina Embeddings API client
│   ├── mcp_tools.py        # Database query tools (sql_query, kb_search, etc.)
│   ├── mock_data.py        # Mock data generation
│   ├── pii_masking.py      # PII protection functions
│   ├── schema.sql         # Database schema + indexes + FK
│   ├── routes/
│   │   ├── ask.py         # POST /ask endpoint
│   │   └── tools.py       # Tool listing endpoints
│   ├── static/
│   │   └── index.html     # Vue 3 frontend (responsive)
│   └── kb_docs/           # Knowledge base markdown files
├── dbt/
│   ├── models/            # dbt transformation models
│   └── tests/             # dbt tests
├── docker-compose.yml    # Container orchestration
├── Dockerfile            # App container image
├── requirements.txt       # Python dependencies
└── bank/                 # Virtual environment (uv)
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web UI |
| `/ask` | POST | Ask a question in natural language |
| `/tools/list` | GET | List available MCP tools |
| `/tools/call` | POST | Call a specific tool |

### Example: Ask a Question

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Top 5 root causes of issues"}'
```

```json
{
  "tool_used": "kpi.top_root_causes",
  "answer": "The top 5 root causes are...",
  "data": [
    {"category": "App Crash", "count": 45, "percentage": 32.14}
  ]
}
```

---

## MCP Tools

| Tool | Description |
|------|-------------|
| `sql.query` | Execute read-only SQL queries |
| `kb.search` | Semantic search over knowledge base |
| `kpi.top_root_causes` | Top 5 issue categories with percentages |

---

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Groq API key (https://console.groq.com)
- Jina API key (https://jina.ai/embeddings)

### Quick Start

```bash
# Clone and configure
cd dBank_Copilot
cp .env.example .env
# Edit .env with your API keys

# Start
docker-compose up --build

# Access
open http://localhost:8000
```

### Example Questions to Try
- "How many customers do we have?"
- "Top 5 root causes of issues"
- "Show me all products"
- "What is Digital Lending?"
- "Tickets after v1.2 release"

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

## Database Schema

### Tables
- `customers` - Customer data
- `products` - Product catalog
- `customer_products` - Customer-product relationships
- `tickets` - Support tickets
- `kb_embeddings` - Vector store for knowledge base

### Performance Indexes
- `idx_tickets_customer_id`, `idx_tickets_product_id`
- `idx_logins_customer_id`
- `idx_customer_products_*`
- `idx_kb_embeddings_embedding` (pgvector)

---

## Running Tests

```bash
# Activate virtual environment
source bank/bin/activate

# Run tests
pytest test_plan_updates_unit.py -v
```

---

## Documentation Files

| File | Description |
|------|-------------|
| `README.md` | This overview |
| `DEVELOPMENT.md` | Development guide and maintenance |
| `PLAN.md` | Implementation plan |
| `TODO.md` | Completed tasks |
| `note.md` | Quick project summary |

---

## Future Improvements

See [TODO.md](./TODO.md) for planned enhancements.

---

*Last updated: April 2026*
