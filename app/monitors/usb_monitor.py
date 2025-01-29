import platform
import psutil
import time
import threading
from app.services.usb_service import UsbDataManager

class USBMonitor:
    def __init__(self):
        self.data_manager = DataManager()
        self.running = False
        self.monitor_thread = None
        self.os_type = platform.system()
        
        if self.os_type == 'Windows':
            try:
                import win32api  # سيتم استيراده فقط عند الحاجة
                self.win32api = win32api
            except ImportError:
                raise Exception("pywin32 package is required for Windows monitoring")
        
        
    def start_monitoring(self):
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        self.running = False
        
    def _monitor_loop(self):
        previous_devices = self._get_connected_devices()
        while self.running:
            current_devices = self._get_connected_devices()
            
            # Detect new devices
            new_devices = [d for d in current_devices if d not in previous_devices]
            for dev in new_devices:
                self._handle_new_device(dev)
                
            # Detect removed devices
            removed_devices = [d for d in previous_devices if d not in current_devices]
            for dev in removed_devices:
                self.data_manager.remove_device(dev['uid'])
                
            previous_devices = current_devices
            time.sleep(2)
            
    def _get_connected_devices(self):
        devices = []
        for part in psutil.disk_partitions():
            if 'removable' in part.opts:
                try:
                    if self.os_type == 'Windows':
                        info = self.win32api.GetVolumeInformation(part.device)
                        device_info = {
                            'uid': f"{info[1]}-{part.device}",
                            'device_id': part.device,
                            'label': info[0],
                            'serial': info[1],
                            'total_size': psutil.disk_usage(part.device).total,
                            'file_system': info[4]
                        }
                    else:  # للأنظمة الأخرى
                        device_info = {
                            'uid': part.device,
                            'device_id': part.device,
                            'label': 'N/A',
                            'serial': 'N/A',
                            'total_size': psutil.disk_usage(part.device).total,
                            'file_system': part.fstype
                        }
                    devices.append(device_info)
                except Exception as e:
                    print(f"Error reading device info: {e}")
        return devices
        
    def _handle_new_device(self, device_info):
        self.data_manager.add_device({
            **device_info,
            'connection_time': datetime.now().isoformat(),
            'vendor': self._get_vendor_info(device_info['serial'])
        })
        
    def _get_vendor_info(self, serial):
        # يمكن إضافة منطق لاستخراج معلومات المزود
        return "Unknown Vendor"
    def __del__(self):
        self.stop_monitoring()