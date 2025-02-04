# app/services/databases/usb_database.py
import sqlite3
from pathlib import Path

class USBDatabase:
    def __init__(self, db_path="data/database.db"):
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS usb_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mac_address TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    event_type TEXT NOT NULL,
                    device TEXT,
                    mountpoint TEXT,
                    fstype TEXT,
                    vendor_id TEXT,
                    product_id TEXT,
                    serial_number TEXT,
                    total_size INTEGER
                )
            ''')
            conn.commit()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def log_event(self, event_data):
        sanitized = []
        for value in event_data:
            if isinstance(value, str):
                if len(value) > 255:
                    value = value[:250] + '...'
                value = value or 'Unknown'
            sanitized.append(value)
        
        query = '''
            INSERT INTO usb_events VALUES (
                NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        '''
        try:
            with self._get_connection() as conn:
                conn.execute(query, tuple(sanitized))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {str(e)}")

    def get_events(self, mac_address, limit=100):
        query = '''
            SELECT id, mac_address, timestamp, event_type, device, mountpoint, 
                fstype, vendor_id, product_id, serial_number, total_size 
            FROM usb_events 
            WHERE mac_address = ?
            ORDER BY timestamp DESC
            LIMIT ?
        '''
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (mac_address, limit))
            return cursor.fetchall()