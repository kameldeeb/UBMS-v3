# File: app/views/process_view.py
import streamlit as st
import pandas as pd
from app.services.process_service import ProcessService
from app.services.device_manager_service import device_manager

def process_monitoring():
    st.header("Process Monitoring")
    device_id = device_manager.device_id
    process_service = ProcessService(device_id)
    
    if st.button("Refresh Process Data"):
        st.experimental_rerun()

    processes = process_service.get_processes()
    if processes:
        df = pd.DataFrame(processes)
        st.dataframe(df)
    else:
        st.info("No process data available.")
