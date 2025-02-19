# File: app/views/usb_view.py
import streamlit as st
import pandas as pd
import json
from streamlit_autorefresh import st_autorefresh
from app.services.usb_service import USBService
from app.utils.device_utils import get_mac_address
import uuid


def bytes_to_human(n):
    symbols = ('B', 'KB', 'MB', 'GB', 'TB', 'PB')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i * 10)
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return f"{value:.2f} {s}"
    return f"{n} B"


def normalize_device_identifier():
    mac_address = get_mac_address()
    try:
        return int(mac_address.replace(":", ""), 16) 
    except ValueError:
        return uuid.getnode() 


def usb_dashboard():
    st.title("USB Monitoring")
    
    if 'usb_service' not in st.session_state:
        device_identifier = normalize_device_identifier()
        st.session_state.usb_service = USBService(device_identifier=device_identifier)
        st.session_state.usb_service.start_monitoring()

    usb_service = st.session_state.usb_service
    
    st_autorefresh(interval=5000, key="usb_refresh")
    
    st.subheader("Connected USB Devices")
    connected_devices = usb_service.get_connected_devices()

    if connected_devices:
        for device in connected_devices:
            device_name = device.get("device", "Unknown")
            mountpoint = device.get("mountpoint", "Unknown")
            fstype = device.get("fstype", "Unknown")
            total_size = device.get("total_size", 0)
            size_str = bytes_to_human(total_size)

            with st.expander(f"Device: {device_name} | Mount: {mountpoint}", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Device:** `{device_name}`")
                    st.markdown(f"**Mountpoint:** `{mountpoint}`")
                with col2:
                    st.markdown(f"**File System:** `{fstype}`")
                    st.markdown(f"**Total Size:** `{size_str}`")
                st.markdown("---")
    else:
        st.info("No USB devices currently connected.")

    st.subheader("Recent USB Events")
    events = usb_service.get_recent_events(limit=100)
    if events:
        event_rows = []
        for event in events:
            details = json.loads(event['details'])
            row = {
                "ID": event["id"],
                "Event Type": event["event_type"],
                "Timestamp": event["timestamp"],
                "Device": details.get("device", "Unknown"),
                "Mountpoint": details.get("mountpoint", "Unknown"),
                "File System": details.get("fstype", "Unknown"),
                "Total Size": bytes_to_human(details.get("total_size", 0))
            }
            event_rows.append(row)
        df_events = pd.DataFrame(event_rows)
        st.dataframe(df_events)
    else:
        st.info("No USB events recorded yet.")


if __name__ == "__main__":
    usb_dashboard()
