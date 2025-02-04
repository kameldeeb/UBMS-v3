import psutil
import platform
import subprocess
import uuid
import time
import json
import logging
from threading import Thread, Event
from datetime import datetime
from app.services.database.db_manager import get_connection

logging.basicConfig(filename='usb_monitor.log', level=logging.DEBUG)

class USBService:
    def __init__(self, device_id):
        self.stop_event = Event()  # Ensure this exists
        self.device_id = device_id
        self.current_devices = []
        self.mac_address = self._get_mac_address()
        self._ensure_device_exists()

    def _ensure_device_exists(self):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM devices WHERE device_identifier = ?", (self.device_id,))
            device = cursor.fetchone()
            if not device:
                cursor.execute(
                    "INSERT INTO devices (device_identifier, name, type, created_at) VALUES (?, ?, ?, datetime('now'))",
                    (self.device_id, "USB Device", "USB"),
                )
                conn.commit()
    
                
    def _get_mac_address(self):
        mac = uuid.getnode()
        return ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))

    def _is_usb_device(self, disk):
        if platform.system() == 'Windows':
            try:
                drive_letter = disk.mountpoint[0] if disk.mountpoint else ''
                cmd = f'''
                    $drive = Get-Partition -DriveLetter '{drive_letter}' -ErrorAction SilentlyContinue | 
                            Get-Disk | 
                            Where-Object {{ $_.BusType -eq 'USB' }}
                    if($drive){{ 'True' }} else {{ 'False' }}
                '''
                result = subprocess.run(
                    ["powershell", "-Command", cmd],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                return 'True' in result.stdout
            except Exception as e:
                logging.error(f"USB detection error: {str(e)}")
                return False
        return 'removable' in disk.opts.lower()

    # app/services/usb_service.py
    def _get_windows_usb_details(self, device_path):
        try:
            cmd = f'''
                $disk = Get-CimInstance Win32_DiskDrive | 
                        Where-Object {{ $_.DeviceID -eq '{device_path}' }}
                
                $props = @{{
                    Vendor = $disk.Manufacturer
                    Product = $disk.Model
                    SerialNumber = $disk.SerialNumber
                    Size = $disk.Size
                }}
                
                $props | ConvertTo-Json
            '''
            result = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0 and result.stdout.strip():
                details = json.loads(result.stdout)
                return {
                    'vendor_id': (details.get('Vendor') or 'Unknown').strip()[:255],
                    'product_id': (details.get('Product') or 'Unknown').strip()[:255],
                    'serial_number': (details.get('SerialNumber') or 'Unknown').strip()[:255],
                    'total_size': int(details.get('Size', 0))
                }
            return {}
        except (subprocess.CalledProcessError, json.JSONDecodeError, TimeoutError) as e:
            logging.error(f"USB details error: {str(e)}")
            return {
                'vendor_id': 'Error',
                'product_id': 'Error',
                'serial_number': 'Error',
                'total_size': 0
            }


    def _get_usb_details(self, device_path):
        if platform.system() == 'Windows':
            return self._get_windows_usb_details(device_path)
        return {}

    def _detect_usb_devices(self):
        current_devices = []
        for disk in psutil.disk_partitions(all=True):
            if self._is_usb_device(disk):
                details = self._get_usb_details(disk.device)
                device_info = {
                    'device': disk.device,
                    'mountpoint': disk.mountpoint,
                    'fstype': disk.fstype,
                    **details
                }
                current_devices.append(device_info)
        return current_devices

    def _monitor_usb(self):
        while not self.stop_event.is_set():
            try:
                self.current_devices = self._detect_usb_devices()
                for dev in self.current_devices:
                    self._log_event("usb_connected", dev)
                time.sleep(3)
            except Exception as e:
                logging.critical(f"Monitoring error: {str(e)}")
                time.sleep(10)

    def _log_event(self, event_type, device_info):
        details = {
            "device": device_info.get('device', 'Unknown'),
            "mountpoint": device_info.get('mountpoint', 'Unknown'),
            "fstype": device_info.get('fstype', 'Unknown'),
            "vendor_id": device_info.get('vendor_id', 'Unknown'),
            "product_id": device_info.get('product_id', 'Unknown'),
            "serial_number": device_info.get('serial_number', 'Unknown'),
            "total_size": device_info.get('total_size', 0)
        }
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO events (device_id, event_category, event_type, timestamp, details)
                VALUES (?, ?, ?, ?, ?)
            """, (self.device_id, "usb", event_type, datetime.now().isoformat(), json.dumps(details)))
            conn.commit()

    def start_monitoring(self):
        self.stop_event.clear()
        monitor_thread = Thread(target=self._monitor_usb, daemon=True)
        monitor_thread.start()

    def stop_monitoring(self):
        self.stop_event.set()

    def get_events(self, limit=100):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM events
                WHERE device_id = ? AND event_category = 'usb'
                ORDER BY timestamp DESC
                LIMIT ?
            """, (self.device_id, limit))
            events = cursor.fetchall()
        return events

    def get_connected_devices(self):
        self.current_devices = self._detect_usb_devices()
        return self.current_devices
