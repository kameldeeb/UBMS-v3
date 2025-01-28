# main.py
import streamlit as st
from app.components.sidebar import sidebar_navigation
from app.pages import monitoring, devices, alerts, analysis, profile, settings
from app.utils.state import init_session_state

# main.py
PAGES = {
    "Real-time Monitoring": monitoring.real_time_monitoring,
    "Device Management": devices.device_management,
    "Alert System": alerts.alert_system,
    "Anomaly Analysis": analysis.anomaly_analysis,
    "User Profile": profile.user_profile,
    "System Settings": settings.system_settings
}

def main():
    st.set_page_config(
        page_title="UBMS Dashboard",
        page_icon="🛡️",
        layout="wide"
    )
    
    init_session_state()
    menu = sidebar_navigation()
    
    if menu in PAGES:
        PAGES[menu]()
    
    # Monitoring status footer
    st.markdown("---")
    active_devices = sum(1 for d in st.session_state.devices['real'] + st.session_state.devices['virtual'] if d['monitoring'])
    status_color = "green" if active_devices else "gray"
    st.markdown(f"""
    <div style="position: fixed; bottom: 10px; right: 10px; 
                padding: 5px 10px; border-radius: 5px; 
                background-color: {status_color}; color: white;">
        Active Devices: {active_devices} | Total Devices: {len(st.session_state.devices['real']) + len(st.session_state.devices['virtual'])}
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()