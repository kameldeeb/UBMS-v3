import sqlite3

# الاتصال بقاعدة بيانات SQLite
conn = sqlite3.connect("اسم_قاعدة_البيانات.db")
cursor = conn.cursor()

# تنفيذ الاستعلام
cursor.execute("SELECT * FROM alerts ORDER BY detected_at DESC LIMIT 50")
results = cursor.fetchall()

# عرض النتائج
for row in results:
    print(row)

# إغلاق الاتصال بقاعدة البيانات
conn.close()
