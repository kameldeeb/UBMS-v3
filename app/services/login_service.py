# app/services/login_service.py
import sqlite3
import getpass
import time
from datetime import datetime, timedelta
from threading import Thread, Event
import uuid
import hashlib

class LoginMonitor:
    def __init__(self):
        self.db_path = "data/database.db"
        self.stop_event = Event()
        self.mac_address = self._get_mac_address()
        self._init_db()
        self.last_event_hash = None  # حفظ الـ hash لآخر حدث مسجل

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS login_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mac_address TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    username TEXT,
                    success INTEGER,
                    source_ip TEXT,
                    auth_method TEXT,
                    os_user TEXT,
                    UNIQUE(mac_address, timestamp, username, success, source_ip, auth_method, os_user)  -- منع التكرار
                )
            ''')
            conn.commit()

    def _get_mac_address(self):
        mac = uuid.getnode()
        return ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))

    def _get_login_events(self):
        current_user = getpass.getuser()
        return [{
            'timestamp': datetime.now(),
            'username': current_user,
            'success': 1,
            'source_ip': '127.0.0.1',
            'auth_method': 'local',
            'os_user': current_user
        }]

    def _generate_event_hash(self, event):
        """ توليد hash من بيانات الحدث لمنع التكرار """
        event_string = f"{event['username']}-{event['success']}-{event['source_ip']}-{event['auth_method']}-{event['os_user']}-{event['timestamp']}"
        return hashlib.sha256(event_string.encode()).hexdigest()

    def _is_duplicate_event(self, event):
        """ التحقق مما إذا كان الحدث مكررًا """
        event_hash = self._generate_event_hash(event)

        if event_hash == self.last_event_hash:
            return True  # حدث مكرر، لا نسجله

        self.last_event_hash = event_hash  # تحديث آخر حدث مسجل
        return False

    def _monitor_logins(self):
        while not self.stop_event.is_set():
            try:
                events = self._get_login_events()
                for event in events:
                    if not self._is_duplicate_event(event):  # منع التكرار
                        self._log_event(event)
                time.sleep(10)
            except Exception as e:
                print(f"Monitoring error: {str(e)}")

    def _log_event(self, event):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR IGNORE INTO login_attempts VALUES (
                        NULL, ?, ?, ?, ?, ?, ?, ?
                    )
                ''', (
                    self.mac_address,
                    event['timestamp'].isoformat(),
                    event['username'],
                    event['success'],
                    event['source_ip'],
                    event['auth_method'],
                    event['os_user']
                ))
                conn.commit()
        except sqlite3.IntegrityError:
            pass  # في حالة التكرار، لا يتم الإدراج

    def start(self):
        self.stop_event.clear()
        Thread(target=self._monitor_logins, daemon=True).start()

    def get_attempts(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM login_attempts 
                WHERE mac_address = ?
                ORDER BY timestamp DESC
            ''', (self.mac_address,))
            return cursor.fetchall()
