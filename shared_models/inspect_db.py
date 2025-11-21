import sqlite3
conn = sqlite3.connect('news_aggregator.db')
cursor = conn.cursor()
cursor.execute("SELECT name, url FROM sources;")
print("Sources:", cursor.fetchall())
conn.close()
