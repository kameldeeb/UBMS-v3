# File: app/services/database/db_manager.py
import sqlite3
from contextlib import contextmanager

DB_PATH = "data/database.db"

@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

def initialize_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        # جدول الأجهزة
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_identifier TEXT UNIQUE,
                name TEXT,
                type TEXT,
                created_at TEXT
            )
        """)
        # جدول الأحداث
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER,
                event_category TEXT,
                event_type TEXT,
                timestamp TEXT,
                details TEXT,
                FOREIGN KEY(device_id) REFERENCES devices(id)
            )
        """)
        # جدول التنبيهات
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER,
                alert_level INTEGER,
                message TEXT,
                timestamp TEXT,
                FOREIGN KEY(device_id) REFERENCES devices(id)
            )
        """)
        conn.commit()
