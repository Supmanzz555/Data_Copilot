# 🏦 Deep Insights Copilot - dBank

> AI-powered support system for dBank's Operation team 

## 📋 Overview

The Deep Insights Copilot is an intelligent system designed to:
- Answer natural-language questions grounded in company data
- Execute safe, parameterized SQL queries via MCP tools

##  Features

### 1. **Data Layer**
-  4 data sources modeled in PostgreSQL (star schema)
  - Customers
  - Tickets
  - Login access
  - Products
- dbt transformations
- Data quality tests

### 2. **Retrieval Layer**
- Vector store using pgvector
- Knowledge base with 9 markdown documents
- Semantic search capabilities

### 3. **LLM Layer (RAG)**
- FastAPI backend with Groq LLM integration
- Context-aware question answering
- Automatic tool selection

### 4. **MCP Server**
Three discoverable tools:
- `sql.query` - Read-only parameterized SQL queries
- `kb.search` - Semantic search over documentation
- `kpi.top_root_causes` - Aggregation for top issues

### 5. **UI**
- Simple chat box for testing bot capability

### 6. **AI Guardrails** 
- **Read-only database access**
- **PII masking** (emails & names automatically masked)
- **Parameterized queries** (SQL injection protection)
- **Tool call logging** (all actions tracked)

## How to test it

### Prerequisites
- Docker & Docker Compose
- **Groq API key** ([Get one here](https://console.groq.com)) - Required

### Setup

1. **Clone the repository**
```bash
cd dBank
```

2. **Configure environment variables**
```bash
# Edit .env and add your Groq API key:
DATABASE_URL=postgresql://admin:admin@db:5432/deep_insights
GROQ_API_KEY=your_groq_api_key_here
```

> **Note**: Embeddings run locally it Uses `sentence-transformers` on CPU

3. **Start the application** 
```bash
docker-compose up --build
```

The system will automatically:
- Wait for the database to be ready
- Create tables and load mock data (if needed)
- Start the FastAPI server

4. **Access the UI**
Open your browser to: **http://localhost:8000**

## 🎯 Example Questions

Try asking the copilot:

1. **"Top 5 root causes of product issues in the previous month by category with % open ticket"**

2. **"Did ticket volume spike after Virtual Bank App v1.2 release?"**

3. **"Write the SQL for churned customers in the last 30, 90 days (not logged in)"**

## 📊 API Endpoints

### Ask a Question
```bash
POST /ask
{
  "question": "What are the top root causes?"
}
```

### List Available Tools
```bash
GET /tools/list
```

### Call a Tool Directly
```bash
POST /tools/call
{
  "name": "kpi.top_root_causes",
  "params": {}
}
```

## 🗂️ Project Structure

```
dBank/
├── app/
│   ├── config.py          # Configuration settings
│   ├── db.py             # Database connection
│   ├── embeddings.py     # KB embedding logic
│   ├── main.py           # FastAPI app entry
│   ├── mcp_tools.py      # MCP tool implementations
│   ├── mock_data.py      # Data generation
│   ├── pii_masking.py    # PII protection
│   ├── schema.sql        # Database schema
│   ├── kb_docs/          # Knowledge base markdown files
│   ├── routes/
│   │   ├── ask.py        # Question answering endpoint
│   │   └── tools.py      # MCP tool endpoints
│   └── static/
│       └── index.html    # Web UI
├── dbt/
│   ├── models/           # dbt transformations
│   └── tests/            # Data quality tests
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Running dbt Transformations

```bash
# Access the app container
docker-compose exec app bash

# Run dbt models
cd dbt
dbt run

# Run tests
dbt test
```

## Stack used

- **Backend**: FastAPI, Python 
- **Database**: PostgreSQL 18 with pgvector extension
- **LLM**: Groq (Compound model)
- **Data Transformation**: dbt
- **Containerization**: Docker & Docker Compose
- **ORM**: SQLAlchemy 


## Doc (KB base topics) (mocking up information for the bots)

- App Release v1.2
- Digital Lending
- Digital Saving
- Known Issues
- Performance Metrics
- Product Policies
- Root Cause Analysis
- Ticket Guidelines
- Troubleshooting

##  Troubleshooting

### Database connection issues
```bash
# Check if DB is running
docker-compose ps

# Restart services
docker-compose restart
```

### Missing Groq API key
Edit `.env` file and add your API key, then restart:
```bash
docker-compose down
docker-compose up
```


**Note**: Replace `your_groq_api_key_here` in `.env` with your actual Groq API key before starting the application.

