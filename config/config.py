# config.py
import os

DATABASES = {
    'login_db': os.path.join(os.path.dirname(__file__), 'data', 'login_attempts.db'),
    'user_db': os.path.join(os.path.dirname(__file__), 'data', 'users.db'),
    'logs_db': os.path.join(os.path.dirname(__file__), 'data', 'logs.db'),
    'usb_db': os.path.join(os.path.dirname(__file__), 'data', 'usb_logs.db'),
    'network_db': os.path.join(os.path.dirname(__file__), 'data', 'logs', 'network_logs.db'),
    'file_db': os.path.join(os.path.dirname(__file__), 'data', 'logs', 'file_logs.db'),
}