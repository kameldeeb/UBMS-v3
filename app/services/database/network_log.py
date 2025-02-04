import sqlite3
import os

# Ensure the database file exists
DB_FILE = "data/logs/network_logs.db"

def create_db():
    """Initialize the SQLite database and create the required table if it doesn't exist."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS network_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_ip TEXT,
                website TEXT,
                start_time TEXT,
                end_time TEXT,
                duration REAL,
                data_usage REAL
            )
        ''')
        conn.commit()

def insert_log(device_ip, website, start_time, end_time, duration, data_usage):
    """Insert a new network log entry into the database."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO network_logs (device_ip, website, start_time, end_time, duration, data_usage)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (device_ip, website, start_time, end_time, duration, data_usage))
        conn.commit()

def get_logs():
    """Retrieve all network logs from the database."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM network_logs ORDER BY start_time DESC')
        return cursor.fetchall()

# Initialize the database on first run
create_db()
