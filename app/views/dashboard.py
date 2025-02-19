import streamlit as st
import pandas as pd
import plotly.express as px
import json
from app.services.db_manager import get_connection
from app.utils.anomaly_detection import detect_anomalies, get_anomaly_summary

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
        df_devices  = pd.read_sql_query("SELECT * FROM devices", conn)
        df_events   = pd.read_sql_query("SELECT * FROM events", conn)
        df_alerts   = pd.read_sql_query("SELECT * FROM alerts", conn)
        df_network  = pd.read_sql_query("SELECT * FROM network_logs", conn)
    
    total_devices   = df_devices.shape[0]
    total_events    = df_events.shape[0]
    total_alerts    = df_alerts.shape[0]
    total_network   = df_network.shape[0]
    total_data_usage = df_network['data_usage'].sum() if not df_network.empty else 0

    # Perform anomaly detection on events
    df_anomaly = detect_anomalies(df_events)
    anomaly_summary = get_anomaly_summary(df_anomaly)
    total_anomalies = anomaly_summary['anomalies'].sum() if not anomaly_summary.empty else 0

    # Summary Metrics Section
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("🖥️ Total Devices", total_devices)
    col2.metric("📂 Total Events", total_events)
    col3.metric("🚨 Total Alerts", total_alerts)
    col4.metric("🌐 Network Logs", total_network)
    col5.metric("💾 Data Usage (bytes)", f"{total_data_usage:,}")

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

    # Anomaly Comparison Chart
    st.markdown("### Anomaly Comparison by Device")
    if not anomaly_summary.empty:
        fig = px.bar(
            anomaly_summary, 
            x='device_id', 
            y='anomalies',
            labels={'device_id': 'Device ID', 'anomalies': 'Anomaly Count'},
            title="Anomaly Points per Device"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No anomaly data available")
    
    st.markdown("---")
    
    # Network Monitoring Chart: Data Usage Over Time
    st.markdown("### Network Data Usage Over Time")
    if not df_network.empty:
        # Convert start_time to datetime and group by date
        df_network['start_time'] = pd.to_datetime(df_network['start_time'], errors='coerce')
        usage_over_time = (
            df_network.groupby(df_network['start_time'].dt.date)['data_usage']
            .sum().reset_index().rename(columns={'start_time': 'Date', 'data_usage': 'Total Data Usage'})
        )
        fig_usage = px.line(usage_over_time, x='Date', y='Total Data Usage', 
                            title="Total Data Usage Over Time", markers=True)
        st.plotly_chart(fig_usage, use_container_width=True)
    else:
        st.info("No network log data available.")
        
    st.markdown("---")
    
    # Recent Events Section 
    st.markdown("### Recent Events")
    if not df_events.empty:
        st.dataframe(df_events.head(10))
    else:
        st.info("No events available.")

if __name__ == "__main__":
    load_dashboard()
