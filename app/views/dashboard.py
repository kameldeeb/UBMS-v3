# File: app/views/dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
from app.services.database.db_manager import get_connection
from app.utils.anomaly_detection import detect_anomalies

def load_dashboard():
    """📊 لوحة تحكم UBMS لعرض الإحصائيات، التحليلات، وكشف الشذوذ."""
    st.title("📊 UBMS Dashboard Overview")
    st.markdown("### 📌 Summary Metrics")

    # تحميل البيانات من قاعدة البيانات
    with get_connection() as conn:
        df_devices = pd.read_sql_query("SELECT * FROM devices", conn)
        df_events = pd.read_sql_query("SELECT * FROM events", conn)
        df_alerts = pd.read_sql_query("SELECT * FROM alerts", conn)

    # حساب الإحصائيات الأساسية
    total_devices = df_devices.shape[0]
    total_events = df_events.shape[0]
    total_alerts = df_alerts.shape[0]
    
    # كشف الشذوذ في البيانات
    total_anomalies = 0
    if not df_events.empty:
        df_events_ai = detect_anomalies(df_events)
        total_anomalies = df_events_ai['anomaly'].eq(-1).sum()

    # عرض الإحصائيات الأساسية
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🖥️ Total Devices", total_devices)
    col2.metric("📂 Total Events", total_events)
    col3.metric("🚨 Total Alerts", total_alerts)
    col4.metric("⚠️ Total Anomalies", total_anomalies)

    st.markdown("---")

    # 📊 أحداث حسب الفئة (Events by Category)
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

    # 📅 الأحداث عبر الزمن (Events Over Time)
    st.markdown("### 📅 Events Over Time")
    if not df_events.empty:
        df_events['timestamp'] = pd.to_datetime(df_events['timestamp'], errors='coerce')
        events_over_time = df_events.groupby(df_events['timestamp'].dt.date).size().reset_index(name="Count")
        events_over_time.rename(columns={'timestamp': 'Date'}, inplace=True)

        fig_time = px.line(
            events_over_time,
            x="Date",
            y="Count",
            title="Events Trend Over Time",
            markers=True,
            labels={"Date": "Date", "Count": "Number of Events"}
        )
        st.plotly_chart(fig_time, use_container_width=True)
    else:
        st.info("No event data available.")

    # 📝 آخر 10 أحداث (Latest 10 Events)
    st.markdown("### 📝 Latest 10 Events")
    if not df_events.empty:
        latest_events = df_events.sort_values("timestamp", ascending=False).head(10)
        st.dataframe(latest_events.style.set_table_styles(
            [{"selector": "th", "props": [("background-color", "#0073e6"), ("color", "white")]}]
        ))
    else:
        st.info("No recent events available.")
