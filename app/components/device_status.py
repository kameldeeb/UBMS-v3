import streamlit as st

def display_active_devices():
    active_devices = sum(
        1 for d in st.session_state.devices['real'] + st.session_state.devices['virtual'] if d['monitoring']
    )
    status_color = "green" if active_devices else "gray"
    st.markdown(f"""
    <div style="position: fixed; bottom: 10px; right: 10px; 
                padding: 5px 10px; border-radius: 5px; 
                background-color: {status_color}; color: white;">
        Active Devices: {active_devices} | Total Devices: {len(st.session_state.devices['real']) + len(st.session_state.devices['virtual'])}
    </div>
    """, unsafe_allow_html=True)
