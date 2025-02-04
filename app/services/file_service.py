# File: app/services/file_service.py
import json
from datetime import datetime
from app.services.database.db_manager import get_connection

class FileService:
    def __init__(self, device_id):
        self.device_id = device_id

    def log_file_event(self, event_type, file_path, file_size, file_hash=None):
        details = {
            "file_path": file_path,
            "file_size": file_size,
            "file_hash": file_hash
        }
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO events (device_id, event_category, event_type, timestamp, details)
                VALUES (?, ?, ?, ?, ?)
            """, (self.device_id, "file", event_type, datetime.now().isoformat(), json.dumps(details)))
            conn.commit()

