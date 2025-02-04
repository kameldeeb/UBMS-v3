# File: app/services/device_manager_service.py
import uuid
from datetime import datetime
from app.services.database.db_manager import get_connection, initialize_db

# تأكد من استدعاء initialize_db() مرة واحدة عند بدء التطبيق
initialize_db()

class DeviceManager:
    def __init__(self):
        self.device_id = None

    def _get_device_identifier(self):
        # يمكن استخدام MAC Address أو توليد UUID جديد
        try:
            import uuid
            mac = uuid.getnode()
            device_identifier = ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))
        except Exception:
            # في حالة حدوث خطأ، يتم توليد UUID
            device_identifier = str(uuid.uuid4())
        return device_identifier

    def register_device(self, name="Main Device", device_type="real"):
        device_identifier = self._get_device_identifier()
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM devices WHERE device_identifier = ?", (device_identifier,))
            row = cursor.fetchone()
            if row:
                self.device_id = row[0]
            else:
                cursor.execute("""
                    INSERT INTO devices (device_identifier, name, type, created_at)
                    VALUES (?, ?, ?, ?)
                """, (device_identifier, name, device_type, datetime.now().isoformat()))
                conn.commit()
                self.device_id = cursor.lastrowid
        return self.device_id

# يمكن استدعاء هذه الخدمة عند بدء التطبيق لتسجيل الجهاز والحصول على معرّف الجهاز
device_manager = DeviceManager()
current_device_id = device_manager.register_device()
