# pages/devices.py
import streamlit as st

def device_management_page():
    st.header("🖥️ Managed Devices")
    
    with st.expander("➕ Add New Device"):
        device_type = st.selectbox("Device Type", ["Virtual", "Physical"])
        name = st.text_input("Device Name")
        
        if st.button("Create Device"):
            device_id = f"{device_type[:4].lower()}-{str(len(st.session_state.devices)+1).zfill(3)}"
            base_path = f"data/{device_type.lower()}_devices/{device_id}"
            
            if device_type == "Virtual":
                add_virtual_device(device_id, name, base_path)
            else:
                pass