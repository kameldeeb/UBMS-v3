# File: app/views/devices.py

import os
import pandas as pd
import streamlit as st
import plotly.express as px
from app.services.device_service import create_virtual_device
from app.services.db_manager import get_connection

def color_score(val):
    """Return a styled color based on the anomaly score."""
    color = 'green' if val < 20 else 'orange' if val < 40 else 'red'
    return f'background-color: {color}; color: white'

def get_all_real_devices():
    """
    Query the database for all real devices.
    Returns a list of device dictionaries.
    """
    with get_connection() as conn:
        df = pd.read_sql_query("SELECT * FROM devices WHERE type='real'", conn)
    return df.to_dict("records")

def device_management():
    st.header("🖥️ Managed Devices")
    
    # Initialize session state for virtual devices if not present.
    if 'virtual_devices' not in st.session_state:
        st.session_state.virtual_devices = []
    
    # Button to create a new virtual device.
    if st.button("Generate Virtual Device"):
        new_device = create_virtual_device()
        st.session_state.virtual_devices.append(new_device)
        st.success(f"Created virtual device: {new_device['name']}")
    
    # Load real devices from the database.
    real_devices = get_all_real_devices()
    # Get virtual devices from session state.
    virtual_devices = st.session_state.virtual_devices
    
    # Combine both lists.
    all_devices = real_devices + virtual_devices
    
    # Ensure each device has an anomaly_score.
    for device in all_devices:
        if 'anomaly_score' not in device:
            device['anomaly_score'] = 0
    
    if all_devices:
        df = pd.DataFrame(all_devices)
        
        # Search box to filter devices by name or identifier.
        search_term = st.text_input("Search Devices", "")
        if search_term:
            df = df[
                df['name'].str.contains(search_term, case=False, na=False) | 
                df['device_identifier'].str.contains(search_term, case=False, na=False)
            ]
        
        # Sort devices by creation date if available.
        if 'created_at' in df.columns:
            df.sort_values(by='created_at', ascending=False, inplace=True)
        
        # Display the device table with anomaly score colored.
        st.dataframe(
            df.style.applymap(color_score, subset=['anomaly_score']),
            use_container_width=True
        )
        
        # Display a pie chart showing the distribution of device types.
        device_counts = df['type'].value_counts().reset_index()
        device_counts.columns = ['Device Type', 'Count']
        st.subheader("Device Distribution")
        fig = px.pie(device_counts, names='Device Type', values='Count', title="Devices by Type")
        st.plotly_chart(fig, use_container_width=True)
        
        # Option to download the device data as CSV.
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Devices Data", data=csv, file_name='devices.csv', mime='text/csv')
    else:
        st.info("No managed devices found.")

def usb_monitoring():
    st.title("USB Device Monitoring")
    
    # Here we simulate USB device data.
    data = {
        'connected': [
            {'device_id': 'USB001', 'vendor': 'VendorA', 'connection_time': '2023-01-01 10:00:00'},
            {'device_id': 'USB002', 'vendor': 'VendorB', 'connection_time': '2023-01-02 11:30:00'}
        ],
        'history': [
            {'device_id': 'USB001', 'connection_time': '2023-01-01 10:00:00', 'disconnection_time': '2023-01-01 12:00:00'},
            {'device_id': 'USB002', 'connection_time': '2023-01-02 11:30:00', 'disconnection_time': '2023-01-02 13:00:00'}
        ]
    }
    
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
