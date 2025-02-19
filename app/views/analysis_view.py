import streamlit as st
import pandas as pd
import altair as alt
import json
from app.utils.anomaly_detection import load_events, detect_anomalies, get_anomaly_summary
from app.services.db_manager import get_connection

def anomaly_analysis():
    st.header("🚨 Anomaly Analysis")
    st.markdown("This page shows the results of anomaly analysis using an Isolation Forest model for anomaly detection on events.")
    
    # --- Anomaly Analysis on Events ---
    df = load_events()
    if df.empty:
        st.info("No event data available for analysis.")
        return
    
    df_anomaly = detect_anomalies(df)
    
    st.subheader("Anomaly Summary per Device")
    summary = get_anomaly_summary(df_anomaly)
    st.dataframe(summary)
    
    st.subheader("Anomalies Over Time")
    df_anomaly['timestamp'] = pd.to_datetime(df_anomaly['timestamp'], errors='coerce')
    anomalies_time = (
        df_anomaly[df_anomaly['anomaly'] == -1]
        .groupby(df_anomaly['timestamp'].dt.date)
        .size()
        .reset_index(name="count")
    )
    
    if not anomalies_time.empty:
        chart = alt.Chart(anomalies_time).mark_line(point=True).encode(
            x=alt.X("timestamp:T", title="Date"),
            y=alt.Y("count:Q", title="Number of Anomalies")
        ).properties(width=600, height=300)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No time anomalies detected.")
    
    st.subheader("Detailed Anomaly Events")
    anomalies = df_anomaly[df_anomaly['anomaly'] == -1].copy()
    
    if 'details' in anomalies.columns:
        try:
            details_expanded = anomalies['details'].apply(lambda x: json.loads(x) if isinstance(x, str) else {})
            details_df = pd.json_normalize(details_expanded)
            duplicate_cols = set(anomalies.columns).intersection(details_df.columns)
            details_df = details_df.rename(columns={col: f"detail_{col}" for col in duplicate_cols})
            anomalies = anomalies.drop(columns=['details']).reset_index(drop=True)
            anomalies = pd.concat([anomalies, details_df], axis=1)
        except Exception as e:
            st.error(f"Error expanding details column: {e}")
    
    st.dataframe(anomalies)
    
    st.markdown("---")
    
    # --- Network Monitoring Overview (from network_logs) ---
    st.subheader("🌐 Network Logs Overview")
    try:
        with get_connection() as conn:
            df_network = pd.read_sql_query("SELECT * FROM network_logs", conn)
    except Exception as e:
        st.error(f"Error loading network logs: {e}")
        df_network = pd.DataFrame()
    
    if df_network.empty:
        st.info("No network log data available.")
    else:
        total_logs = df_network.shape[0]
        total_usage = df_network['data_usage'].sum()
        st.metric("Total Network Logs", total_logs)
        st.metric("Total Data Usage (bytes)", f"{total_usage:,}")
        
        df_network['start_time'] = pd.to_datetime(df_network['start_time'], errors='coerce')
        usage_over_time = (
            df_network.groupby(df_network['start_time'].dt.date)['data_usage']
            .sum().reset_index().rename(columns={'start_time': 'Date', 'data_usage': 'Total Data Usage'})
        )
        chart_network = alt.Chart(usage_over_time).mark_line(point=True).encode(
            x=alt.X("Date:T", title="Date"),
            y=alt.Y("Total Data Usage:Q", title="Data Usage (bytes)")
        ).properties(width=600, height=300)
        st.altair_chart(chart_network, use_container_width=True)

if __name__ == "__main__":
    anomaly_analysis()
