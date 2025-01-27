# app/pages/devices.py
import os
import json
import pandas as pd
import streamlit as st

def color_score(val):
    color = 'green' if val < 20 else 'orange' if val < 40 else 'red'
    return f'background-color: {color}; color: white'

def device_management():
    st.header("🖥️ Managed Devices")
    
    # Add virtual device
    if st.button("➕ Generate Virtual Device"):
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
    
    # Device list table
    all_devices = st.session_state.devices['real'] + st.session_state.devices['virtual']
    
    # Ensure all devices have 'anomaly_score'
    for device in all_devices:
        device.setdefault('anomaly_score', 0)  # Default value if missing
    
    df = pd.DataFrame(all_devices)
    
    # Apply conditional formatting if column exists
    if 'anomaly_score' in df.columns:
        st.dataframe(
            df.style.applymap(color_score, subset=['anomaly_score']),
            use_container_width=True
        )
    else:
        st.warning("The 'anomaly_score' column does not exist in the device data.")
