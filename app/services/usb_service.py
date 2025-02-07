# File: app/services/usb_service.py
import psutil
import ctypes
import time
import json
import logging
import uuid
from datetime import datetime
from threading import Thread, Event
from pathlib import Path
from app.services.db_manager import get_connection, init_db, register_device  

log_dir = Path("data/log")
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename='data/log/usb_monitor.log', 
    level=logging.DEBUG, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

init_db()

def is_removable_drive(mountpoint):
    try:
        drive_type = ctypes.windll.kernel32.GetDriveTypeW(mountpoint)
        # DRIVE_REMOVABLE = 2
        return drive_type == 2
    except Exception as e:
        logging.error(f"Error checking drive type for {mountpoint}: {e}")
        return False

def get_drive_size(mountpoint):

    try:
        usage = psutil.disk_usage(mountpoint)
        return usage.total
    except Exception as e:
        logging.error(f"Error getting disk usage for {mountpoint}: {e}")
        return 0

class USBService:
    def __init__(self, device_identifier):

        self.stop_event = Event()
        self.device_identifier = device_identifier
        self.device_id = register_device(device_identifier, name="USB Monitoring Device", device_type="USB")
        self.current_devices = {}
        self.mac_address = self._get_mac_address()

    def _get_mac_address(self):
        mac = uuid.getnode()
        return ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))

    def _detect_usb_devices(self):

        devices = {}
        for partition in psutil.disk_partitions(all=False):
            if partition.mountpoint and is_removable_drive(partition.mountpoint):
                total_size = get_drive_size(partition.mountpoint)
                devices[partition.mountpoint] = {
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total_size": total_size
                }
        return devices

    def _log_event(self, event_type, device_info):

        details = {
            "device": device_info.get("device", "Unknown"),
            "mountpoint": device_info.get("mountpoint", "Unknown"),
            "fstype": device_info.get("fstype", "Unknown"),
            "total_size": device_info.get("total_size", 0)
        }
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO events (device_id, event_category, event_type, timestamp, details)
                    VALUES (?, ?, ?, ?, ?)
                """, (self.device_id, "usb", event_type, datetime.now().isoformat(), json.dumps(details)))
                conn.commit()
        except Exception as e:
            logging.error(f"Error logging event: {e}")

    def _monitor_usb(self):
        while not self.stop_event.is_set():
            try:
                new_devices = self._detect_usb_devices()
                new_keys = set(new_devices.keys())
                old_keys = set(self.current_devices.keys())

                for key in new_keys - old_keys:
                    logging.info(f"USB connected: {new_devices[key]}")
                    self._log_event("usb_connected", new_devices[key])
                for key in old_keys - new_keys:
                    logging.info(f"USB disconnected: {self.current_devices[key]}")
                    self._log_event("usb_disconnected", self.current_devices[key])

                self.current_devices = new_devices
                time.sleep(5)
            except Exception as e:
                logging.error(f"Error in monitoring: {e}")
                time.sleep(10)

    def start_monitoring(self):

        if not hasattr(self, "monitor_thread") or not self.monitor_thread.is_alive():
            self.stop_event.clear()
            self.monitor_thread = Thread(target=self._monitor_usb, daemon=True)
            self.monitor_thread.start()

    def stop_monitoring(self):
        self.stop_event.set()

    def get_connected_devices(self):

        return list(self.current_devices.values())

    def get_recent_events(self, limit=100):

        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, device_id, event_category, event_type, timestamp, details
                    FROM events
                    WHERE device_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (self.device_id, limit))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logging.error(f"Error fetching events: {e}")
            return []
