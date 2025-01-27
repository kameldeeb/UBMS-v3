# app/utils/state.py
import streamlit as st
import os
import json
from app.monitors.file_monitor import FileMonitor


def init_session_state():
    if 'selected_folders' not in st.session_state:
        st.session_state.selected_folders = []  # تهيئة قائمة المجلدات
    
    if 'file_monitoring' not in st.session_state:
        st.session_state.file_monitoring = False  # تهيئة حالة المراقبة

    if 'devices' not in st.session_state:
        st.session_state.devices = {
            'real': [{
                'id': 'real-001',
                'name': 'Main Device',
                'anomaly_score': 15,
                'monitoring': False,
                'folders': [],
                'data_path': '../../data/real_devices'
            }],
            'virtual': []
        }



    if 'alerts' not in st.session_state:
        st.session_state.alerts = []
    if 'global_monitoring' not in st.session_state:
        st.session_state.global_monitoring = False

def add_virtual_device():
    new_device = {
        'id': f"virt-{len(st.session_state.devices['virtual'])+1:03d}",
        'name': f"Virtual Device {len(st.session_state.devices['virtual'])+1}",
        'anomaly_score': 35,
        'monitoring': False,
        'folders': [],
        'data_path': f"../../data/virtual_devices/virt-{len(st.session_state.devices['virtual'])+1:03d}"
    }
    st.session_state.devices['virtual'].append(new_device)
    os.makedirs(new_device['data_path'], exist_ok=True)
    print(f"Created directory: {new_device['data_path']}")
