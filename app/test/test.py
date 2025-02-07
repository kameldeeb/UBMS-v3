import sqlite3

conn = sqlite3.connect("data/databases.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM alerts ORDER BY detected_at DESC LIMIT 50")
results = cursor.fetchall()

for row in results:
    print(row)

conn.close()
