# app/monitors/file_monitor.py
import json
import time
import hashlib
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, output_path):
        super().__init__()
        self.output_path = output_path
        self.log_file = Path(output_path) / "file_changes.json"
        self.log_file.touch(exist_ok=True)

    def _record_event(self, event_type, src_path):
        try:
            file_stats = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "file_path": str(src_path),
                "file_size": Path(src_path).stat().st_size if Path(src_path).is_file() else 0,
                "file_hash": self._calculate_file_hash(src_path) if Path(src_path).is_file() else None
            }
            
            with open(self.log_file, "a") as f:
                f.write(json.dumps(file_stats) + "\n")
                
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
    def __init__(self, folders_to_watch, output_path):
        self.observer = Observer()
        self.handler = FileChangeHandler(output_path)
        self.folders = folders_to_watch
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