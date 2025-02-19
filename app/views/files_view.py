# File: app/views/file_view.py
import streamlit as st
import pandas as pd
import json
import os
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from streamlit_autorefresh import st_autorefresh
from app.services.file_service import FileMonitor, get_recent_file_events
from threading import Thread

DATA_DIR = Path("data")
FOLDERS_CONFIG = DATA_DIR / "selected_folders.json"

def ensure_config():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_folders():
    try:
        ensure_config()
        if FOLDERS_CONFIG.exists():
            with open(FOLDERS_CONFIG, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        st.error(f"Error loading folders: {str(e)}")
        return []

def save_folders(folders):
    try:
        ensure_config()
        with open(FOLDERS_CONFIG, 'w') as f:
            json.dump(folders, f, indent=2)
    except Exception as e:
        st.error(f"Error saving folders: {str(e)}")

def select_folder_gui():
    try:
        root = tk.Tk()
        root.withdraw()
        root.wm_attributes('-topmost', 1)
        folder_path = filedialog.askdirectory(parent=root)
        root.update()
        root.destroy()
        return folder_path
    except Exception as e:
        st.error(f"Folder selection error: {str(e)}")
        return None

def real_time_monitoring():
    st.header("File Monitoring")
    
    if 'selected_folders' not in st.session_state:
        st.session_state.selected_folders = load_folders()
    else:
        st.session_state.selected_folders = load_folders()
    
    if 'folder_input_value' not in st.session_state:
        st.session_state.folder_input_value = ""

    with st.expander("📁 File Monitoring Configuration", expanded=True):
        with st.form(key="folder_form"):
            cols = st.columns([0.7, 0.1, 0.1])  

            with cols[0]:
                new_folder = st.text_input(
                    "Enter folder path:",
                    help="Type path or click browse",
                    key="folder_input",
                    label_visibility="collapsed",
                    placeholder="📂 Enter folder path or click browse...",
                    value=st.session_state.folder_input_value
                )            
            with cols[1]:
                browse_clicked = st.form_submit_button(
                    "🌐 Browse",
                    use_container_width=True,
                    help="Select folder from dialog"
                )
            with cols[2]:
                add_clicked = st.form_submit_button(
                    "➕ Add",
                    use_container_width=True,
                    help="Add folder to monitoring list",
                    type="primary"
                )
            
            # Event Handling
            if browse_clicked:
                selected = select_folder_gui()
                if selected:
                    st.session_state.folder_input_value = selected
                    st.rerun()
            
            if add_clicked:
                if new_folder:
                    if os.path.isdir(new_folder):
                        if new_folder not in st.session_state.selected_folders:
                            st.session_state.selected_folders.append(new_folder)
                            save_folders(st.session_state.selected_folders)
                            st.success(f"Added: {new_folder}")
                            st.session_state.folder_input_value = ""
                        else:
                            st.warning("Folder already in list")
                    else:
                        st.error("Invalid folder path")
                else:
                    st.warning("Please enter a folder path")

        st.subheader("📂 Active Monitoring Folders")
        # Validate active monitoring folders: remove any folder that no longer exists
        valid_folders = []
        removed_folders = []
        for folder in st.session_state.selected_folders:
            if os.path.isdir(folder):
                valid_folders.append(folder)
            else:
                removed_folders.append(folder)

        if removed_folders:
            st.warning(f"Removed invalid folders: {', '.join(removed_folders)}")
            st.session_state.selected_folders = valid_folders
            save_folders(valid_folders)
            
        if not st.session_state.selected_folders:
            st.info("No folders being monitored.  Please add a folder for monitoring.")
        else:
            for idx, folder in enumerate(st.session_state.selected_folders):
                cols = st.columns([0.8, 0.1])
                with cols[0]:
                    st.code(folder, language='text')
                with cols[1]:
                    if st.button(
                        "🗑️", 
                        key=f"remove_{idx}",
                        help="Remove folder from monitoring",
                        type="secondary"
                    ):
                        st.session_state.selected_folders.pop(idx)
                        save_folders(st.session_state.selected_folders)
                        st.rerun()  
            
            st.markdown(f"<div style='text-align:right;color:#666'>Total: {len(st.session_state.selected_folders)} folders</div>", 
                        unsafe_allow_html=True)

        st.markdown("---")
        status_cols = st.columns([0.4, 0.6])
        with status_cols[0]:
            status = "ACTIVE 🟢" if st.session_state.get('file_monitoring') else "INACTIVE 🔴"
            st.markdown(f"**Monitoring Status:** `{status}`")
        with status_cols[1]:
            if st.session_state.get('file_monitoring'):
                if st.button("⏹️ Stop Monitoring", 
                             type="primary", 
                             use_container_width=True,
                             help="Stop all monitoring activities"):
                    st.session_state.file_monitor.stop()
                    st.session_state.file_monitoring = False
                    st.success("Monitoring stopped successfully!")
            else:
                if st.session_state.selected_folders:
                    device_id = 0  
                    st.session_state.file_monitor = FileMonitor(
                        folders_to_watch=st.session_state.selected_folders,
                        output_path="data/real_devices",
                        device_id=device_id
                    )
                    monitor_thread = Thread(target=st.session_state.file_monitor.start)
                    monitor_thread.daemon = True
                    monitor_thread.start()
                    st.session_state.file_monitoring = True
                    st.success("Monitoring started automatically!")
                else:
                    st.error("Please add folders to monitor first")


    st.markdown("---")
    st_autorefresh(interval=5000, key="table_autorefresh")
    st.subheader("🕒 Recent File Changes")
    try:
        file_events = get_recent_file_events(limit=15)
        if file_events:
            df = pd.DataFrame(file_events)
            df = df[['timestamp', 'event_type', 'file_path', 'file_size']]            
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df = df.dropna(subset=['timestamp'])
            df = df.sort_values(by='timestamp', ascending=False)
            df = df.head(15)
            df = df.drop_duplicates(subset=['event_type', 'file_path'], keep='first')
            df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
            df['file_size'] = df['file_size'].apply(lambda x: f"{round(x/1024, 2)} KB" if pd.notna(x) and x > 0 else "N/A")

            st.dataframe(
                df.style.applymap(
                    lambda x: "color: #4CAF50" if x.upper() == "CREATED" else 
                              "color: #f44336" if x.upper() == "DELETED" else 
                              "color: #FFC107" if x.upper() == "MODIFIED" else "",
                    subset=['event_type']
                ),
                column_config={
                    "timestamp": "Time",
                    "event_type": "Event",
                    "file_path": "Path",
                    "file_size": "Size"
                },
                use_container_width=True,
                hide_index=True,
                height=400
            )
        else:
            st.info("No file changes detected yet")
    except Exception as e:
        st.error(f"Error displaying changes: {str(e)}")

if __name__ == "__main__":
    real_time_monitoring()
