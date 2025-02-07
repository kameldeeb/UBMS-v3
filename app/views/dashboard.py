# File: app/views/dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import json
from app.services.db_manager import get_connection
from app.utils.anomaly_detection import detect_anomalies

def format_details(details):
    try:
        if isinstance(details, str):
            details = json.loads(details)
        return json.dumps(details, indent=2, ensure_ascii=False)
    except Exception as e:
        return details

def load_dashboard():
    st.title("📊 UBMS Dashboard Overview")
    st.markdown("### 📌 Summary Metrics")

    with get_connection() as conn:
        df_devices = pd.read_sql_query("SELECT * FROM devices", conn)
        df_events = pd.read_sql_query("SELECT * FROM events", conn)
        df_alerts = pd.read_sql_query("SELECT * FROM alerts", conn)

    total_devices = df_devices.shape[0]
    total_events = df_events.shape[0]
    total_alerts = df_alerts.shape[0]
    
    total_anomalies = 0
    if not df_events.empty:
        df_events_ai = detect_anomalies(df_events)
        total_anomalies = df_events_ai['anomaly'].eq(-1).sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🖥️ Total Devices", total_devices)
    col2.metric("📂 Total Events", total_events)
    col3.metric("🚨 Total Alerts", total_alerts)
    col4.metric("⚠️ Total Anomalies", total_anomalies)

    st.markdown("---")

    st.markdown("### 📊 Events by Category")
    if not df_events.empty:
        events_by_category = df_events['event_category'].value_counts().reset_index()
        events_by_category.columns = ["Event Category", "Count"]

        fig_category = px.bar(
            events_by_category,
            x="Event Category",
            y="Count",
            color="Event Category",
            text="Count",
            title="Events by Category",
            labels={"Event Category": "Event Type", "Count": "Occurrences"}
        )
        fig_category.update_layout(showlegend=False)
        st.plotly_chart(fig_category, use_container_width=True)
    else:
        st.info("No event data available.")

    st.markdown("### 📝 Latest 10 Events")
    if not df_events.empty:
        df_events['details_formatted'] = df_events['details'].apply(format_details)
        
        latest_events = df_events.sort_values("timestamp", ascending=False).head(10)
        
        st.dataframe(
            latest_events[[
                'id',
                'device_id',
                'event_category',
                'event_type',
                'timestamp',
                'details_formatted',
                'anomaly'
            ]].style.set_table_styles(
                [{"selector": "th", "props": [("background-color", "#0073e6"), ("color", "white")]}]
            )
        )
    else:
        st.info("No recent events available.")
