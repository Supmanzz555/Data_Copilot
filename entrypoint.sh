#!/bin/bash
set -e

echo "Deep Insights Copilot - Starting..."

# wait for db
echo "Waiting for database..."
python << END
import time
import sys
from sqlalchemy import create_engine, text
from app.config import settings

max_retries = 30
for i in range(max_retries):
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(" Database is ready!")
        sys.exit(0)
    except Exception as e:
        print(f" Waiting for database... ({i+1}/{max_retries})")
        time.sleep(2)

print("Database not available")
sys.exit(1)
END

# check if tables exist, if not creaet 
echo "Checking database..."
python << END
from sqlalchemy import create_engine, text, inspect
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
inspector = inspect(engine)
tables = inspector.get_table_names()

if 'customers' not in tables:
    print("Initializing database with mock data...")
    from app.mock_data import generate_mock_data
    generate_mock_data()
    print("Database initialized!")
else:
    print("Database already initialized (found existing tables)")

# Check if KB is loaded
with engine.connect() as conn:
    kb_count = conn.execute(text("SELECT COUNT(*) FROM kb_embeddings")).scalar()
    if kb_count == 0:
        print("📚 Loading knowledge base documents...")
        from app.embeddings import load_kb_documents
        load_kb_documents()
    else:
        print(f"Knowledge base already loaded ({kb_count} documents)")
END

echo "🚀 Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

