import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import os
from dotenv import load_dotenv

# Load from the API directory
load_dotenv('C:/Users/DELL/Desktop/GN/simple web - antigravity/sudan-news-api/.env')

db_url = os.getenv('DATABASE_URL')
print(f"DATABASE_URL from .env: {db_url}")

# Parse the SQLite path
if db_url.startswith('sqlite:///'):
    db_path = db_url.replace('sqlite:///', '')
    print(f"Parsed database path: {db_path}")
    print(f"Exists: {os.path.exists(db_path)}")
