# File: app/services/login_service.py
import getpass
import uuid
import time
from datetime import datetime
from threading import Thread, Event  
from app.services.db_manager import register_device, log_login_attempt, get_connection

class LoginMonitor:
    def __init__(self):
        self.stop_event = Event()
        self.mac_address = self._get_mac_address()
        self.device_id = register_device(self.mac_address, name="Login Monitor Device", device_type="login")
        self.logged = False

    def _get_mac_address(self):
        mac = uuid.getnode()
        return ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))

    def _get_login_event_details(self):
        current_user = getpass.getuser()
        event_id = f"{self.mac_address}-{current_user}-{int(datetime.now().timestamp())}"
        return {
            'timestamp': datetime.now().isoformat(),
            'event_id': event_id,
            'event_type': 'login',
            'username': current_user,
            'success': 1,
            'ip': 'N/A',
            'method': 'N/A',
            'os_user': 'N/A'
        }

    def _monitor_logins(self):
        if not self.logged:
            try:
                details = self._get_login_event_details()
                log_login_attempt(
                    device_id=self.device_id,
                    event_id=details['event_id'],
                    event_type=details['event_type'],
                    username=details['username'],
                    success=details['success'],
                    ip=details['ip'],
                    method=details['method'],
                    os_user=details['os_user'],
                    timestamp=details['timestamp']
                )
                log_event(
                    device_id=self.device_id,
                    event_category="login", 
                    event_type=details['event_type'],
                    details=details,        
                    timestamp=details['timestamp']
                )
                self.logged = True
            except Exception as e:
                print(f"Monitoring error: {str(e)}")
        while not self.stop_event.is_set():
            time.sleep(10)


    def start(self):
        self.stop_event.clear()
        Thread(target=self._monitor_logins, daemon=True).start()

    def stop(self):
        self.stop_event.set()

    def get_attempts(self):

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, device_id, event_id, event_type, username, success, ip, method, os_user, timestamp
                FROM login_attempts
                WHERE device_id = ?
                ORDER BY timestamp DESC
            """, (self.device_id,))
            attempts = cursor.fetchall()
        return [dict(row) for row in attempts]

