import sqlite3
from config.config import DATABASES

DB_PATH = "data/login_attempts.db"

def create_login_attempts_table():
    conn = sqlite3.connect("data/login_attempts.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS login_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mac_address TEXT NOT NULL,
            event_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            username TEXT NOT NULL,
            success INTEGER DEFAULT 0,
            ip TEXT,
            method TEXT,
            os_user TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()



def get_last_event_id(mac_address):
    with sqlite3.connect("data/login_attempts.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT event_id FROM login_attempts WHERE mac_address = ? ORDER BY id DESC LIMIT 1", (mac_address,))
        row = cursor.fetchone()
        return row[0] if row else None

def log_event(event):
    with sqlite3.connect("data/login_attempts.db") as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO login_attempts (mac_address, timestamp, event_id, event_type, username, success, ip, method, os_user)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event['mac_address'],
                event['timestamp'],
                event['event_id'],
                event['event_type'],
                event['username'],
                event.get('success', 1),      # مثال: اعتبار النجاح افتراضياً
                event.get('ip', 'N/A'),
                event.get('method', 'N/A'),
                event.get('os_user', 'N/A')
            ))
            conn.commit()
        except sqlite3.IntegrityError:
            pass

