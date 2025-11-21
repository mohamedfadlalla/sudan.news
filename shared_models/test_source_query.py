"""
Simple database query to verify source details
"""
import sys
import io
# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import sqlite3

conn = sqlite3.connect('news_aggregator.db')
cursor = conn.cursor()

# Get a cluster with articles
cursor.execute("""
    SELECT c.id, c.title, COUNT(ca.article_id) as article_count
    FROM clusters c
    JOIN cluster_articles ca ON c.id = ca.cluster_id
    GROUP BY c.id
    LIMIT 1
""")

cluster_row = cursor.fetchone()
if not cluster_row:
    print("No clusters with articles found")
    exit()

cluster_id, cluster_title, article_count = cluster_row
print(f"Cluster ID: {cluster_id}")
print(f"Cluster Title: {cluster_title}")
print(f"Article Count: {article_count}")
print("\n" + "="*80 + "\n")

# Get first article from this cluster with source details
cursor.execute("""
    SELECT 
        a.headline,
        s.name as source_name,
        s.url as source_url,
        s.bias,
        s.owner,
        s.founded_at,
        s.hq_location
    FROM articles a
    JOIN cluster_articles ca ON a.id = ca.article_id
    JOIN sources s ON a.source_id = s.id
    WHERE ca.cluster_id = ?
    LIMIT 1
""", (cluster_id,))

article_row = cursor.fetchone()
if article_row:
    headline, source_name, source_url, bias, owner, founded, hq = article_row
    print("First Article in Cluster:")
    print(f"  Headline: {headline[:50]}...")
    print(f"  Source Name: {source_name}")
    print(f"  Source URL: {source_url}")
    print(f"  Bias: {bias}")
    print(f"  Owner: {owner}")
    print(f"  Founded: {founded}")
    print(f"  HQ: {hq}")
    print("\n" + "="*80)
    print("SUCCESS! Source details are in the database and can be queried.")
else:
    print("No article found")

conn.close()
