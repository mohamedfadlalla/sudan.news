import sqlite3
import json

conn = sqlite3.connect('news_aggregator.db')
cursor = conn.cursor()

# Get a sample of sources with all their details
cursor.execute("""
    SELECT name, url, language, owner, founded_at, hq_location, bias 
    FROM sources 
    LIMIT 5
""")

print("Sample of sources with details:")
print("="*80)
for row in cursor.fetchall():
    name, url, lang, owner, founded, hq, bias = row
    print(f"Name: {name}")
    print(f"  URL: {url}")
    print(f"  Language: {lang}")
    print(f"  Owner: {owner}")
    print(f"  Founded: {founded}")
    print(f"  HQ: {hq}")
    print(f"  Bias: {bias}")
    print("-"*80)

# Count by bias
cursor.execute("SELECT bias, COUNT(*) FROM sources GROUP BY bias")
print("\nBias distribution:")
print("="*80)
for bias, count in cursor.fetchall():
    print(f"{bias}: {count}")

conn.close()
