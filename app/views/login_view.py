# File: app/views/login_view.py
import streamlit as st
import pandas as pd
import time
from app.services.login_service import LoginMonitor

def login_monitoring():
    st.header("Login Monitoring")
    
    if 'login_service' not in st.session_state:
        st.session_state.login_service = LoginMonitor()
        st.session_state.login_service.start()

    col1, col2, col3 = st.columns(3)
    attempts = st.session_state.login_service.get_attempts()
    
    with col1:
        st.metric("Total Attempts", len(attempts))
    
    with col2:
        success = len([a for a in attempts if a.get("success") == 1])
        st.metric("Successful Logins", success)
    
    with col3:
        failed = len([a for a in attempts if a.get("success") == 0])
        st.metric("Failed Attempts", failed)

    # Filters
    st.subheader("🔍 Filter Options")
    with st.expander("Advanced Filters"):
        col_a, col_b = st.columns(2)
        
        with col_a:
            success_filter = st.selectbox(
                "Login Status:",
                ["All", "Success", "Failure"]
            )
        
        with col_b:
            time_filter = st.date_input(
                "Filter by Date:",
                []
            )

    st.subheader("🕒 Login Attempt History")
    time.sleep(1)
    if not attempts:
        st.info("No login attempts recorded")
        return

    df = pd.DataFrame(attempts)
    
    df.rename(columns={
        "id": "ID",
        "device_id": "Device ID",
        "event_id": "Event ID",
        "event_type": "Event Type",
        "username": "Username",
        "success": "Success",
        "ip": "IP",
        "method": "Method",
        "os_user": "OS User",
        "timestamp": "Timestamp"
    }, inplace=True)
    
    if success_filter == "Success":
        df = df[df['Success'] == 1]
    elif success_filter == "Failure":
        df = df[df['Success'] == 0]

    st.dataframe(
        df,
        column_config={
            'Timestamp': st.column_config.DatetimeColumn(),
            'Success': st.column_config.CheckboxColumn(
                label="Success",
                default=False
            ),
            'IP': "Source IP",
            'Method': "Auth Method"
        },
        use_container_width=True,
        hide_index=True,
        height=500
    )

    if failed > 3:
        st.error(f"⚠️ Multiple failed login attempts detected ({failed})")

if __name__ == "__main__":
    login_monitoring()
