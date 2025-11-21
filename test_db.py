#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

db_url = os.getenv('DATABASE_URL', 'sqlite:///news_aggregator.db')
print(f"Database URL: {db_url}")

try:
    engine = create_engine(db_url, echo=True)
    with engine.connect() as conn:
        from sqlalchemy import text
        result = conn.execute(text("SELECT COUNT(*) FROM clusters"))
        count = result.fetchone()[0]
        print(f"Clusters count: {count}")
    print("Database connection successful!")
except Exception as e:
    print(f"Error: {e}")
