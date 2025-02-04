# File: app/views/analysis_view.py
import streamlit as st
import pandas as pd
import altair as alt
from app.utils.anomaly_detection import load_events, detect_anomalies, get_anomaly_summary

def anomaly_analysis():
    """
    Anomaly Analysis Page:
    Displays a summary of anomalies with charts and detailed anomaly events.
    Place this code in: app/views/analysis_view.py
    """
    st.header("🚨 Anomaly Analysis")
    st.markdown("This page shows the results of anomaly analysis using a machine learning model.")
    
    # Load event data from the database
    df = load_events()
    if df.empty:
        st.info("No event data available for analysis.")
        return
    
    # Apply the anomaly detection model to the data
    df_anomaly = detect_anomalies(df)
    
    # Display anomaly summary for each device
    st.subheader("Anomaly Summary per Device")
    summary = get_anomaly_summary(df_anomaly)
    st.dataframe(summary)
    
    # Plot anomalies over time
    st.subheader("Anomalies Over Time")
    # Convert the 'timestamp' column to datetime
    df_anomaly['timestamp'] = pd.to_datetime(df_anomaly['timestamp'], errors='coerce')
    
    # Filter the anomalies and group them by date to count occurrences
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
    
    # Display detailed anomaly event information
    st.subheader("Detailed Anomaly Events")
    anomalies = df_anomaly[df_anomaly['anomaly'] == -1]
    st.dataframe(anomalies)
