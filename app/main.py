import streamlit as st
import warnings
warnings.filterwarnings("ignore", message=".*missing ScriptRunContext.*")

st.set_page_config(
    page_title="UBMS Dashboard",
    page_icon="🛡️",
    layout="wide"
)

from app.components.sidebar import sidebar_navigation
from app.components.device_status import display_active_devices
from app.utils.state import init_session_state
from app.views import (
    alerts_view, analysis_view, devices_view, files_view,
    settings_view, dashboard, usb_view, login_view, process_view
)
from views.network_view import network_monitoring

def get_pages():
    return {
        "Dashboard": dashboard.load_dashboard,
        "Anomaly Analysis": analysis_view.anomaly_analysis,
        "Device Management": devices_view.device_management,
        "Alert System": alerts_view.alert_system,
        "File Monitoring": files_view.real_time_monitoring,
        "USB Monitoring": usb_view.usb_dashboard,
        "Login Monitoring": login_view.login_monitoring,
        "Process Monitoring": process_view.process_monitoring,
        "System Settings": settings_view.system_settings,
        "Network Monitoring": network_monitoring, 
    }

def main():
    init_session_state()
    menu = sidebar_navigation()
    pages = get_pages()

    if menu in pages:
        pages[menu]()

    display_active_devices()

if __name__ == "__main__":
    main()
