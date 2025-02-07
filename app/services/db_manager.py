# File: app/services/db_manager.py
import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path("data/database.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initializes the unified database with all required tables:
      - devices (master table)
      - events (for general events, e.g. USB, process snapshots, etc.)
      - alerts
      - login_attempts
      - network_logs
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        # Master Devices Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_identifier TEXT UNIQUE,
                name TEXT,
                type TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Unified Events Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER,
                event_category TEXT,
                event_type TEXT,
                timestamp DATETIME,
                details TEXT,
                FOREIGN KEY(device_id) REFERENCES devices(id)
            )
        """)
        # Unified Alerts Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER,
                alert_level INTEGER,
                message TEXT,
                timestamp DATETIME,
                FOREIGN KEY(device_id) REFERENCES devices(id)
            )
        """)
        # Unified Login Attempts Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER,
                event_id TEXT,
                event_type TEXT,
                username TEXT,
                success INTEGER DEFAULT 0,
                ip TEXT,
                method TEXT,
                os_user TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(device_id) REFERENCES devices(id)
            )
        """)
        # Unified Network Logs Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS network_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER,
                device_ip TEXT,
                website TEXT,
                start_time DATETIME,
                end_time DATETIME,
                duration REAL,
                data_usage REAL,
                FOREIGN KEY(device_id) REFERENCES devices(id)
            )
        """)
        conn.commit()

# -----------------------------
# Device Management Functions
# -----------------------------
def register_device(device_identifier, name="Main Device", device_type="real"):
    """
    Registers a device (or retrieves its id if already registered) in the devices table.
    
    :param device_identifier: Unique identifier for the device (e.g., MAC address)
    :param name: Human-friendly device name.
    :param device_type: Type of device (for categorization).
    :return: The device's primary key id.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM devices WHERE device_identifier = ?", (device_identifier,))
        row = cursor.fetchone()
        if row:
            return row["id"]
        else:
            cursor.execute("""
                INSERT INTO devices (device_identifier, name, type, created_at)
                VALUES (?, ?, ?, ?)
            """, (device_identifier, name, device_type, datetime.now().isoformat()))
            conn.commit()
            return cursor.lastrowid

def get_device(device_id):
    """
    Retrieves a device record by its primary key.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM devices WHERE id = ?", (device_id,))
        return cursor.fetchone()

# -----------------------------
# Event Logging Functions
# -----------------------------
def log_event(device_id, event_category, event_type, details, timestamp=None):
    """
    Logs a general event (e.g., USB connected/disconnected, process snapshot, etc.)
    into the events table.
    
    :param device_id: Foreign key to the devices table.
    :param event_category: Category of the event (e.g., 'usb', 'process', etc.)
    :param event_type: Specific event type (e.g., 'usb_connected').
    :param details: A dictionary with event details (will be stored as JSON).
    :param timestamp: Optional timestamp; if omitted, uses current time.
    """
    timestamp = timestamp or datetime.now().isoformat()
    details_json = json.dumps(details)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO events (device_id, event_category, event_type, timestamp, details)
            VALUES (?, ?, ?, ?, ?)
        """, (device_id, event_category, event_type, timestamp, details_json))
        conn.commit()

def get_recent_events(device_id, limit=100):
    """
    Retrieves the most recent events for a device.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM events
            WHERE device_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (device_id, limit))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

# -----------------------------
# Alert Logging Functions
# -----------------------------
def log_alert(device_id, alert_level, message, timestamp=None):
    """
    Logs an alert into the alerts table.
    
    :param alert_level: Severity level (integer).
    :param message: Alert message text.
    """
    timestamp = timestamp or datetime.now().isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO alerts (device_id, alert_level, message, timestamp)
            VALUES (?, ?, ?, ?)
        """, (device_id, alert_level, message, timestamp))
        conn.commit()

def get_alerts(device_id, limit=100):
    """
    Retrieves recent alerts for a device.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM alerts
            WHERE device_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (device_id, limit))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

# -----------------------------
# Login Attempt Logging Functions
# -----------------------------
def log_login_attempt(device_id, event_id, event_type, username, success, ip, method, os_user, timestamp=None):
    """
    Logs a login attempt into the login_attempts table.
    """
    timestamp = timestamp or datetime.now().isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO login_attempts (device_id, event_id, event_type, username, success, ip, method, os_user, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (device_id, event_id, event_type, username, success, ip, method, os_user, timestamp))
        conn.commit()

def get_login_attempts(device_id, limit=100):
    """
    Retrieves recent login attempts for a device.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM login_attempts
            WHERE device_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (device_id, limit))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

# -----------------------------
# Network Log Functions
# -----------------------------
def log_network_log(device_id, device_ip, website, start_time, end_time, duration, data_usage):
    """
    Logs a network usage record into the network_logs table.
    
    :param device_ip: The IP address of the device.
    :param website: The remote website or domain.
    :param start_time: Start time of the session.
    :param end_time: End time of the session.
    :param duration: Duration of the session (in seconds or minutes).
    :param data_usage: Data usage in bytes (or any consistent unit).
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO network_logs (device_id, device_ip, website, start_time, end_time, duration, data_usage)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (device_id, device_ip, website, start_time, end_time, duration, data_usage))
        conn.commit()

def get_network_logs(device_id, limit=100):
    """
    Retrieves recent network logs for a device.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM network_logs
            WHERE device_id = ?
            ORDER BY start_time DESC
            LIMIT ?
        """, (device_id, limit))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

# -----------------------------
# Initialization and Testing
# -----------------------------
init_db()

if __name__ == '__main__':
    sample_identifier = "00:11:22:33:44:55"  
    device_id = register_device(sample_identifier, name="Test Device", device_type="test")
    print(f"Registered device id: {device_id}")

    log_event(device_id, "usb", "usb_connected", {
        "device": "USB1",
        "mountpoint": "E:\\",
        "fstype": "FAT32",
        "total_size": 16000000000
    })

    # Log a sample alert.
    log_alert(device_id, alert_level=1, message="Test alert message")

    # Log a sample login attempt.
    log_login_attempt(device_id, "EVT001", "login", "admin", 1, "192.168.1.10", "password", "admin")

    # Log a sample network log.
    now_iso = datetime.now().isoformat()
    log_network_log(device_id, "192.168.1.10", "example.com", now_iso, now_iso, 60.0, 1024.0)

    # Retrieve and print the logged data.
    print("Recent events:", get_recent_events(device_id))
    print("Alerts:", get_alerts(device_id))
    print("Login attempts:", get_login_attempts(device_id))
    print("Network logs:", get_network_logs(device_id))
