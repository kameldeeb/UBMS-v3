# File: app/services/file_service.py
import json
import hashlib
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
from app.services.db_manager import get_connection

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, device_id):
        super().__init__()
        self.device_id = device_id  
    def _record_event(self, event_type, src_path):
        try:
            file_path = str(src_path)
            file_obj = Path(src_path)
            file_size = file_obj.stat().st_size if file_obj.is_file() else 0
            file_hash = self._calculate_file_hash(src_path) if file_obj.is_file() else None

            event_details = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "file_path": file_path,
                "file_size": file_size,
                "file_hash": file_hash
            }

            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO events (device_id, event_category, event_type, timestamp, details)
                    VALUES (?, 'file', ?, ?, ?)
                """, (
                    self.device_id,
                    event_type,
                    datetime.now().isoformat(),
                    json.dumps(event_details)
                ))
                conn.commit()
        except Exception as e:
            print(f"Error logging file event: {e}")

    def _calculate_file_hash(self, file_path):
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"Error calculating hash: {e}")
            return None

    def on_created(self, event):
        self._record_event("CREATED", event.src_path)

    def on_modified(self, event):
        self._record_event("MODIFIED", event.src_path)

    def on_deleted(self, event):
        self._record_event("DELETED", event.src_path)


class FileMonitor:
    def __init__(self, folders_to_watch, device_id, output_path=None):

        self.observer = Observer()
        self.device_id = device_id
        self.folders = folders_to_watch
        self.output_path = output_path
        self.handler = FileChangeHandler(device_id=self.device_id)
        self.is_monitoring = False

    def start(self):
        if not self.is_monitoring:
            for folder in self.folders:
                self.observer.schedule(self.handler, folder, recursive=True)
            self.observer.start()
            self.is_monitoring = True

    def stop(self):
        if self.is_monitoring:
            self.observer.stop()
            self.observer.join()
            self.is_monitoring = False


def get_recent_file_events(limit=15):

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timestamp, event_type, details FROM events
                WHERE event_category = 'file'
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            events = []
            for row in rows:
                event = dict(row)
                try:
                    details = json.loads(event.get("details", "{}"))
                except Exception:
                    details = {}
                event["file_path"] = details.get("file_path", "N/A")
                event["file_size"] = details.get("file_size", 0)
                events.append(event)
            return events
    except Exception as e:
        print(f"Error retrieving recent file events: {e}")
        return []
