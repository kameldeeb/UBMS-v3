# File: app/services/device_service.py
import os
import random
import string
from datetime import datetime
from app.services.db_manager import get_connection, register_device

def generate_virtual_device_identifier():
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"VIRT-{suffix}"

def create_virtual_device():

    device_identifier = generate_virtual_device_identifier()
    device_name = f"Virtual Device {device_identifier.split('-')[-1]}"
    
    device_id = register_device(device_identifier, name=device_name, device_type="virtual")
    
    anomaly_score = random.randint(10, 50)
    
    data_path = f"data/virtual_devices/{device_identifier}"
    os.makedirs(data_path, exist_ok=True)
    
    
    virtual_device = {
        'id': device_id, 
        'device_identifier': device_identifier,
        'name': device_name,
        'anomaly_score': anomaly_score,
        'monitoring': False, 
        'folders': [],  
        'data_path': data_path,
        'created_at': datetime.now().isoformat()
    }
    return virtual_device

def get_all_managed_devices(real_devices, virtual_devices):
    return real_devices + virtual_devices
