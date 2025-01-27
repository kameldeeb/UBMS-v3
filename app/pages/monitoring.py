# app/pages/monitoring.py
import streamlit as st
import pandas as pd
import json
import os
from app.monitors.file_monitor import FileMonitor
from threading import Thread

def start_device_monitoring(device):
    if not device['monitoring'] and device['folders']:
        device['monitor'] = FileMonitor(
            folders_to_watch=device['folders'],
            output_path=device['data_path']
        )
        monitor_thread = Thread(target=device['monitor'].start)
        monitor_thread.daemon = True
        monitor_thread.start()
        device['monitoring'] = True

def stop_device_monitoring(device):
    if device['monitoring']:
        device['monitor'].stop()
        device['monitoring'] = False

def real_time_monitoring():
    st.header("🔍 Live Monitoring Panel")
    
    # File monitoring controls
    with st.expander("📁 File Monitoring Configuration", expanded=True):
        col1, col2 = st.columns([3,1])
        with col1:
            new_folder = st.text_input("Add folder to monitor", "C:/Users/Public/Documents")
            if st.button("Add Folder"):
                if os.path.exists(new_folder):
                    st.session_state.selected_folders.append(new_folder)
                else:
                    st.error("Invalid folder path")
        
        with col2:
            st.markdown("## Current Folders")
            for folder in st.session_state.selected_folders:
                st.markdown(f"- `{folder}`")
                
        if st.button("🚀 Start File Monitoring" if not st.session_state.get('file_monitoring', False) else "⏹️ Stop File Monitoring"):
            if not st.session_state.file_monitoring:
                if st.session_state.selected_folders:
                    st.session_state.file_monitor = FileMonitor(
                        folders_to_watch=st.session_state.selected_folders,
                        output_path="data/real_devices"
                    )
                    monitor_thread = Thread(target=st.session_state.file_monitor.start)
                    monitor_thread.daemon = True
                    monitor_thread.start()
                    st.session_state.file_monitoring = True
                    st.success("File monitoring started!")
                else:
                    st.error("Select at least one folder first")
            else:
                st.session_state.file_monitor.stop()
                st.session_state.file_monitoring = False
                st.success("File monitoring stopped!")

    # عرض آخر التغييرات
    st.subheader("Recent File Changes")
    try:
        with open("data/real_devices/file_changes.json", "r") as f:
            lines = f.readlines()[-10:]  # عرض آخر 10 أحداث
            if lines:
                data = [json.loads(line) for line in lines]
                df = pd.DataFrame(data)
                st.dataframe(
                    df[['timestamp', 'event_type', 'file_path', 'file_size']],
                    use_container_width=True
                )
            else:
                st.info("No file changes detected yet")
    except FileNotFoundError:
        st.info("Monitoring data not available")
