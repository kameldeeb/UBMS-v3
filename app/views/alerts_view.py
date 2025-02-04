# app/pages/alerts.py
import streamlit as st
from datetime import datetime

def alert_system():
    st.header("Active Alerts")
    
    # Alert configuration
    with st.expander("⚙️ Alert Settings"):
        col1, col2 = st.columns(2)
        with col1:
            alert_threshold = st.slider("Alert Threshold", 0, 100, 40)
            st.checkbox("Enable Email Notifications", True)
        with col2:
            st.text_input("Notification Email", "security@company.com")
            st.button("Save Configuration")
    
    # Alerts display
    if st.session_state.alerts:
        for alert in st.session_state.alerts[-5:]:
            st.error(f"⏰ {alert['time']} | {alert['message']}")
    else:
        st.info("No active alerts")