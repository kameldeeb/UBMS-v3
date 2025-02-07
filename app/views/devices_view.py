# File: app/views/devices.py
import os
import pandas as pd
import streamlit as st
from app.services.device_service import create_virtual_device, get_all_managed_devices

def color_score(val):
    color = 'green' if val < 20 else 'orange' if val < 40 else 'red'
    return f'background-color: {color}; color: white'

def device_management():
    st.header("🖥️ Managed Devices")
    
    if 'devices' not in st.session_state:
        st.session_state.devices = {
            'real': [],       
            'virtual': []
        }
    
    if st.button("Generate Virtual Device"):
        new_device = create_virtual_device()
        st.session_state.devices['virtual'].append(new_device)
        st.success(f"Created virtual device: {new_device['name']}")
    
    all_devices = get_all_managed_devices(st.session_state.devices['real'],
        st.session_state.devices['virtual'])
    
    for device in all_devices:
        device.setdefault('anomaly_score', 0)
    
    if all_devices:
        df = pd.DataFrame(all_devices)
        if 'anomaly_score' in df.columns:
            st.dataframe(
                df.style.applymap(color_score, subset=['anomaly_score']),
                use_container_width=True
            )
        else:
            st.warning("The 'anomaly_score' column does not exist in the device data.")
    else:
        st.info("No managed devices found.")

def usb_monitoring():
    st.title("USB Device Monitoring")
    
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = get_all_devices  
    
    data = st.session_state.data_manager()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Connected USB Devices")
        if data['connected']:
            for device in data['connected']:
                st.json({
                    "Device ID": device['device_id'],
                    "Vendor": device['vendor'],
                    "Connected Since": device['connection_time']
                })
        else:
            st.info("No USB devices connected")
    
    with col2:
        st.subheader("Connection History")
        history_df = pd.DataFrame(data['history'])
        if not history_df.empty:
            st.dataframe(
                history_df[['device_id', 'connection_time', 'disconnection_time']],
                height=400
            )
        else:
            st.info("No USB connection history available")

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Select Page", ["Managed Devices", "USB Monitoring"])
    
    if page == "Managed Devices":
        device_management()
    elif page == "USB Monitoring":
        usb_monitoring()

if __name__ == "__main__":
    main()
