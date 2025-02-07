# app/services/device_monitor_services.py
import time
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Thread
from pathlib import Path

class DeviceMonitor(Thread):
    def __init__(self, device_id):
        super().__init__(daemon=True)
        self.device_id = device_id
        self.active = True
        self.observer = Observer()
        
    def run(self):
        device_dir = Path(f"data/devices/{self.device_id}")
        log_file = device_dir / "activity.log"
        
        class MonitorHandler(FileSystemEventHandler):
            def on_any_event(self, event):
                log_entry = {
                    "timestamp": time.time(),
                    "event_type": event.event_type,
                    "file_path": event.src_path,
                    "device_id": self.device_id
                }
                with open(log_file, 'a') as f:
                    f.write(json.dumps(log_entry) + '\n')
        
        config = self.load_config()
        for folder in config['folders']:
            self.observer.schedule(MonitorHandler(), folder, recursive=True)
        
        self.observer.start()
        while self.active:
            time.sleep(1)
        
    def stop(self):
        self.active = False
        self.observer.stop()
        self.observer.join()