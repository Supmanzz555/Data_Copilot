# dBank_Copilot - Project Summary

## Overview
AI-powered support system for dBank's Operations team - answers natural-language questions grounded in company data and executes safe SQL queries.

## Tech Stack
- **Backend**: FastAPI + Python
- **Database**: PostgreSQL + pgvector
- **LLM**: Groq
- **Frontend**: Vue 3 + Tailwind CSS (dark mode)

## Key Files
| File | Description |
|------|-------------|
| `app/main.py` | FastAPI entry point |
| `app/config.py` | Pydantic settings |
| `app/database.py` | Sync + async DB engines |
| `app/routes/ask.py` | `/ask` endpoint |
| `app/mcp_tools.py` | SQL, KB search, KPI tools |
| `app/schema.sql` | Schema + indexes + FK |
| `app/static/index.html` | Vue 3 frontend |

## Quick Start
```bash
# Configure
cp .env.example .env  # Add GROQ_API_KEY, JINA_API_KEY

# Run
docker-compose up --build

# Access
http://localhost:8000
```

## Features
- Natural language to SQL
- Knowledge base semantic search
- Rate limiting (10/min)
- PII masking
- Dark mode support

## Full Docs
See [DEVELOPMENT.md](./DEVELOPMENT.md)