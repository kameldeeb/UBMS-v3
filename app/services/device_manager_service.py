# app/core/device_manager.py
import json
from pathlib import Path
import tkinter as tk
from tkinter import filedialog

class DeviceManager:
    def __init__(self):
        self.DEVICES_DIR = Path("data/devices")
        self.DEVICES_DIR.mkdir(parents=True, exist_ok=True)
    
    def get_devices_list(self):
        """Retrieve list of all devices"""
        devices = []
        for device_dir in self.DEVICES_DIR.iterdir():
            config_file = device_dir / "config.json"
            if config_file.exists():
                with open(config_file) as f:
                    devices.append(json.load(f))
        return devices
    
    def get_device(self, device_id):
        """Get full device details"""
        device_dir = self.DEVICES_DIR / device_id
        config_file = device_dir / "config.json"
        if config_file.exists():
            with open(config_file) as f:
                return json.load(f)
        return None
    
    def update_device(self, device_id, updates):
        """Update device configuration"""
        device_dir = self.DEVICES_DIR / device_id
        config_file = device_dir / "config.json"
        
        if config_file.exists():
            with open(config_file, 'r+') as f:
                config = json.load(f)
                config.update(updates)
                f.seek(0)
                json.dump(config, f, indent=2)
                f.truncate()
    
    def select_folder_gui(self):
        """GUI folder selection"""
        root = tk.Tk()
        root.withdraw()
        root.wm_attributes('-topmost', 1)
        folder_path = filedialog.askdirectory(parent=root)
        root.destroy()
        return folder_path