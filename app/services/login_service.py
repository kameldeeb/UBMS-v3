import sqlite3
import getpass
import uuid
import time
from datetime import datetime
from threading import Thread, Event  
import platform
import subprocess
from app.services.database.login_database import get_last_event_id, log_event, DB_PATH

class LoginMonitor:
    def __init__(self):
        self.stop_event = Event()
        self.mac_address = self._get_mac_address()
        self.logged = False

    def _get_mac_address(self):
        mac = uuid.getnode()
        return ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))

    def _get_login_event(self):
        current_user = getpass.getuser()
        event_id = f"{self.mac_address}-{current_user}-{int(datetime.now().timestamp())}"
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_id': event_id,
            'mac_address': self.mac_address,
            'event_type': 'login',
            'username': current_user,
            'success': 1,
            'ip': 'N/A',
            'method': 'N/A',
            'os_user': 'N/A'
        }
        return event

    def _monitor_logins(self):
        if not self.logged:
            try:
                event = self._get_login_event()
                log_event(event)
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
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, mac_address, timestamp, username, success, ip, method, os_user
                FROM login_attempts
                ORDER BY id DESC
            """)
            attempts = cursor.fetchall()
        return attempts
