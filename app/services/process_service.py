# app/services/process_service.py
import psutil
import json
from datetime import datetime
from app.services.database.db_manager import get_connection

class ProcessService:
    def __init__(self, device_id):
        self.device_id = device_id

    def get_processes(self):
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return processes

    def log_process_snapshot(self):
        processes = self.get_processes()
        snapshot = {
            "processes": processes
        }
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO events (device_id, event_category, event_type, timestamp, details)
                VALUES (?, 'process', 'snapshot', ?, ?)
            """, (self.device_id, datetime.now().isoformat(), json.dumps(snapshot)))
            conn.commit()
        return processes
