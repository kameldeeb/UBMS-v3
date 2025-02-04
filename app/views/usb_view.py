# app/views/usb_view.py
import streamlit as st
import pandas as pd
import uuid
from app.services.usb_service import USBService

import time

def usb_dashboard():
    st.header("USB Monitoring")

    if 'usb_service' not in st.session_state:
        st.session_state.usb_service = USBService(device_id=str(uuid.getnode()))
        st.session_state.usb_service.start_monitoring()
    
    usb_service = st.session_state.usb_service
    
    connected_devices = usb_service.get_connected_devices()

    status_cols = st.columns(3)
    status_cols[0].markdown("**Monitoring Status:** 🟢 Active")
    status_cols[1].markdown(f"**MAC Address:** `{usb_service.mac_address}`")
    status_cols[2].button("Refresh Devices", on_click=lambda: st.rerun())


    st.subheader("Connected USB Devices")
    
    if connected_devices:
        df = pd.DataFrame(connected_devices)
        st.table(df)  
    else:
        st.warning("⚠️ No USB devices detected")

    
    # Event history section
    st.subheader("Historical Events")
    events = usb_service.get_events()
    
    if not events:
        st.info("No events recorded yet")
    else:
        df = pd.DataFrame(events, columns=[
            'ID', 'MAC Address', 'Timestamp', 'Type', 
            'Device', 'Mountpoint', 'Filesystem',
            'Vendor ID', 'Product ID', 'Serial Number', 
            'Size (Bytes)'
        ])
        
        # Convert and clean data
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df['Size (GB)'] = df['Size (Bytes)'].apply(lambda x: x/1e9 if x > 0 else 0)
        max_size = df['Size (GB)'].max() or 1  # Prevent division by zero
        
        # Configure dataframe display
        st.dataframe(
            df,
            column_config={
                'Timestamp': st.column_config.DatetimeColumn(
                    'Time',
                    format="YYYY-MM-DD HH:mm:ss"
                ),
                'Type': st.column_config.SelectboxColumn(
                    "Event Type",
                    options=["connected", "disconnected"],
                    required=True
                ),
                'Size (GB)': st.column_config.ProgressColumn(
                    "Storage Size",
                    help="Device capacity in gigabytes",
                    format="%.2f GB",
                    min_value=0,
                    max_value=max_size
                )
            },
            use_container_width=True,
            hide_index=True,
            height=500
        )