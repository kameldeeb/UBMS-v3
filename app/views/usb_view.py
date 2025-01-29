# app/views/usb_dashboard.py
import streamlit as st
import pandas as pd
import numpy as np
from app.services.usb_service import USBService

def usb_dashboard():
    st.header("🔌 USB Monitoring")
    usb_service = USBService() 
    # Initialize service and auto-start monitoring
    usb_service = st.session_state.get('usb_service')
    if not usb_service:
        usb_service = USBService()
        usb_service.start_monitoring()
        st.session_state.usb_service = usb_service

    # Current status
    st.markdown(f"**Monitoring Status:** 🟢 Active (Automatic)")

    # Current devices
    st.subheader("📌 Connected Devices")
    if not usb_service.current_devices:
        st.info("No USB devices connected")
    else:
        for dev in usb_service.current_devices:
            with st.expander(f"{dev['device']} - {dev.get('vendor_id', 'Unknown')}"):
                cols = st.columns(2)
                with cols[0]:
                    st.metric("Mount Point", dev['mountpoint'])
                    st.metric("File System", dev['fstype'])
                with cols[1]:
                    st.metric("Total Size", f"{dev.get('total_size', 0)/1e9:.2f} GB")
                    st.metric("Serial Number", dev.get('serial_number', 'Unknown'))

    # Historical events
    st.subheader("🕒 Event History")
    events = usb_service.get_events()
    
    if not events:
        st.info("No events recorded")
        return
    
    df = pd.DataFrame(events, columns=[
        'ID', 'MAC Address', 'Timestamp', 'Type', 'Device', 
        'Mountpoint', 'Filesystem', 'Vendor ID', 'Product ID', 
        'Serial Number', 'Size'
    ])


    df = df.applymap(lambda x: int(x) if isinstance(x, (np.int64, np.int32)) else x)

    df['Size'] = pd.to_numeric(df['Size'], errors='coerce').fillna(0).replace([np.inf, -np.inf], 0)
    



    
    if not df['Size'].isnull().all() and df['Size'].max() != np.inf:
        st.dataframe(
            df,
            column_config={
                'Timestamp': 'Time',
                'Type': st.column_config.SelectboxColumn(
                    options=["connected", "disconnected"]
                ),
                'Size': st.column_config.ProgressColumn(
                    format="%.2f GB",
                    min_value=0,
                    max_value=df['Size'].max()
                )
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.error("🚨 Error: Invalid values detected in 'Size' column")


    # Filters
    event_type = st.selectbox("Filter events:", ["All", "connected", "disconnected"])
    if event_type != "All":
        df = df[df['Type'] == event_type]

    # Display
    st.dataframe(
        df,
        column_config={
            'Timestamp': 'Time',
            'Type': st.column_config.SelectboxColumn(
                options=["connected", "disconnected"]
            ),
            'Size': st.column_config.ProgressColumn(
                format="%.2f GB",
                min_value=0,
                max_value=df['Size'].max()
            )
        },
        use_container_width=True,
        hide_index=True
    )