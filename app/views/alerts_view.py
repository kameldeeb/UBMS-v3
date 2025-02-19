# File: app/views/alert_view.py

import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
from app.services.db_manager import get_alerts
from app.services.device_manager_service import device_manager

st_autorefresh(interval=10000, key="alert_autorefresh")

def alert_system():
    st.header("Active Alerts")
    
    # -------------------------------
    # Dynamic Alert Configuration Panel
    # -------------------------------
    with st.expander("⚙️ Alert Settings", expanded=True):
        if 'alert_config' not in st.session_state:
            st.session_state.alert_config = {
                "alert_threshold": 40,             
                "min_alert_level": 0,              
                "email_notifications": True,
                "notification_email": "security@company.com"
            }
        config = st.session_state.alert_config
        
        col1, col2 = st.columns(2)
        with col1:
            config["alert_threshold"] = st.slider("Alert Threshold", 0, 100, config["alert_threshold"])
            config["min_alert_level"] = st.slider("Minimum Alert Level to Display", 0, 100, config["min_alert_level"])
        with col2:
            config["email_notifications"] = st.checkbox("Enable Email Notifications", config["email_notifications"])
            config["notification_email"] = st.text_input("Notification Email", config["notification_email"])
        
        if st.button("Save Configuration"):
            st.session_state.alert_config = config
            st.success("Alert configuration saved.")
    
    # -------------------------------
    # Retrieve and Filter Alerts
    # -------------------------------
    current_device_id = device_manager.device_id
    alerts = get_alerts(current_device_id, limit=200)
    
    if alerts:
        df_alerts = pd.DataFrame(alerts)
        
        if 'alert_level' in df_alerts.columns:
            df_alerts = df_alerts[df_alerts['alert_level'] >= config["min_alert_level"]]
        
        # -------------------------------
        # Styled Alerts Table
        # -------------------------------
        def color_alert_level(val):
            if isinstance(val, (int, float)):
                if val >= 70:
                    return 'background-color: red; color: white;'
                elif val >= 40:
                    return 'background-color: orange;'
                else:
                    return 'background-color: green; color: white;'
            return ''
        
        styled_df = df_alerts.style.applymap(color_alert_level, subset=['alert_level'])
        st.subheader("Alerts Table")
        st.dataframe(styled_df, height=400)
        
        # -------------------------------
        # Alerts Summary Chart
        # -------------------------------
        if 'alert_level' in df_alerts.columns:
            df_alerts['Level Range'] = pd.cut(
                df_alerts['alert_level'],
                bins=[-1, 40, 70, 100],
                labels=["Low", "Medium", "High"]
            )
            summary = df_alerts['Level Range'].value_counts().reset_index()
            summary.columns = ['Alert Level', 'Count']
            fig = px.bar(summary, x='Alert Level', y='Count',
                         title="Alert Count by Level",
                         color='Alert Level',
                         text='Count')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No active alerts.")

if __name__ == "__main__":
    alert_system()
