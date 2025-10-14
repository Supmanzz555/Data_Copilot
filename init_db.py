#!/usr/bin/env python3
"""
Database initialization script for Deep Insights Copilot
Runs schema creation and mock data generation
"""

import time
import sys
from app.mock_data import generate_mock_data

def wait_for_db(max_retries=30):
    """Wait for database to be ready"""
    from sqlalchemy import create_engine, text
    from app.config import settings
    
    for i in range(max_retries):
        try:
            engine = create_engine(settings.DATABASE_URL)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Database is ready!")
            return True
        except Exception as e:
            print(f" Waiting for database... ({i+1}/{max_retries})")
            time.sleep(2)
    
    print("Database not available after maximum retries")
    return False

if __name__ == "__main__":
    print("Deep Insights Copilot - Database Initialization")
    print("=" * 60)
    
    if not wait_for_db():
        sys.exit(1)
    
    print("\n📊 Generating mock data...")
    try:
        generate_mock_data()
        print("Mock data generated successfully!")
        print("\nSetup complete! Access the app at http://localhost:8000")
    except Exception as e:
        print(f"Error generating data: {e}")
        sys.exit(1)

