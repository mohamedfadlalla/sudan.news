import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import sqlite3
import os

# Check both database files
db_paths = [
    'C:/Users/DELL/Desktop/GN/simple web - antigravity/shared_models/news_aggregator.db',
    'C:/Users/DELL/Desktop/GN/simple web - antigravity/news_aggregator.db'
]

for db_path in db_paths:
    if os.path.exists(db_path):
        print(f"\n{'='*80}")
        print(f"Database: {db_path}")
        print(f"Exists: YES")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get sources table schema
        cursor.execute("PRAGMA table_info(sources)")
        columns = cursor.fetchall()
        
        column_names = [col[1] for col in columns]
        print(f"Columns in sources table: {', '.join(column_names)}")
        
        has_new_columns = all(col in column_names for col in ['owner', 'founded_at', 'hq_location', 'bias'])
        print(f"Has new columns: {'YES ✓' if has_new_columns else 'NO ✗'}")
        
        conn.close()
    else:
        print(f"\n{'='*80}")
        print(f"Database: {db_path}")
        print(f"Exists: NO")

print(f"\n{'='*80}")
