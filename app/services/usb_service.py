# app/services/usb_service.py
import sqlite3
import psutil
from pathlib import Path
from datetime import datetime
from threading import Thread, Event
import platform
import subprocess
import uuid
import time

class USBService:
    def __init__(self):
        self.db_path = Path("data/database.db")
        self.stop_event = Event()
        self.current_devices = []
        self._init_db()
        self.mac_address = self._get_mac_address()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
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

    def _get_mac_address(self):
        mac = uuid.getnode()
        return ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))

    def _get_usb_details(self, device_path):
        try:
            if platform.system() == 'Windows':
                cmd = f"wmic diskdrive where DeviceID='{device_path}' get /value"
                output = subprocess.check_output(cmd, shell=True).decode()
                details = {}
                for line in output.split('\n'):
                    if '=' in line:
                        key, value = line.strip().split('=')
                        details[key.lower()] = value
                return {
                    'vendor_id': details.get('vendor', ''),
                    'product_id': details.get('product', ''),
                    'serial_number': details.get('serialnumber', ''),
                    'total_size': int(details.get('size', 0))
                }
            else:
                return {}
        except Exception as e:
            print(f"Error getting USB details: {str(e)}")
            return {}


    def _monitor_usb(self):
        last_check = []
        while not self.stop_event.is_set():
            try:
                current = []
                for disk in psutil.disk_partitions(all=True):  
                    if 'removable' in disk.opts.lower() or 'usb' in disk.device.lower():
                        details = self._get_usb_details(disk.device)
                        current.append({
                            **details,
                            'device': disk.device,
                            'mountpoint': disk.mountpoint,
                            'fstype': disk.fstype
                        })

                if current != last_check:
                    for dev in current:
                        if dev not in self.current_devices:
                            self._log_event('connected', dev)
                    for dev in self.current_devices:
                        if dev not in current:
                            self._log_event('disconnected', dev)

                    self.current_devices = current
                    last_check = current.copy()

                time.sleep(5)  

            except Exception as e:
                print(f"Monitoring error: {str(e)}")

    def _log_event(self, event_type, device_info):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO usb_events VALUES (
                    NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            ''', (
                self.mac_address,
                datetime.now().isoformat(),
                event_type,
                device_info.get('device'),
                device_info.get('mountpoint'),
                device_info.get('fstype'),
                device_info.get('vendor_id'),
                device_info.get('product_id'),
                device_info.get('serial_number'),
                device_info.get('total_size')
            ))
            conn.commit()

    def start_monitoring(self):
        self.stop_event.clear()
        Thread(target=self._monitor_usb, daemon=True).start()

    def get_events(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, mac_address, timestamp, event_type, device, mountpoint, 
                    fstype, vendor_id, product_id, serial_number, total_size 
                FROM usb_events 
                WHERE mac_address = ?
                ORDER BY timestamp DESC
                LIMIT 100
            ''', (self.mac_address,))
            
            events = cursor.fetchall()
            
            clean_events = []
            for event in events:
                event = list(event)  
                if event[-1] is None or event[-1] in [float('inf'), float('-inf')]:
                    event[-1] = 0
                clean_events.append(event)
            
            return clean_events
