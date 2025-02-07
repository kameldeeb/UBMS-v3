# File: app/views/process_view.py
import streamlit as st
import pandas as pd
from app.services.process_service import ProcessService
from app.services.device_manager_service import device_manager  
def process_monitoring():
    st.header("Process Monitoring")
    device_id = device_manager.device_id  
    process_service = ProcessService(device_id)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Log Process Snapshot"):
            process_service.log_process_snapshot()
            st.success("Process snapshot has been logged.")
            st.session_state.rerun = not st.session_state.get("rerun", False)
    
    with col2:
        if st.button("Refresh Process Data"):
            st.session_state.rerun = not st.session_state.get("rerun", False)
    
    processes = process_service.get_logged_snapshot()
    if processes:
        df = pd.DataFrame(processes)
        st.dataframe(df)
    else:
        st.info("No logged process data available. Click 'Log Process Snapshot' to record a snapshot.")

if __name__ == "__main__":
    process_monitoring()
