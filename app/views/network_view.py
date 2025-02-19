# File: app/views/network_view.py

import streamlit as st
import pandas as pd
import plotly.express as px
import threading
import time
import uuid 
from scapy.all import get_if_list
from streamlit_autorefresh import st_autorefresh
from app.utils.device_utils import get_mac_address
from app.services.network_service import start_packet_capture, analyze_network_traffic
from app.services.db_manager import get_network_logs, init_db, register_device



# --- Session State Initialization for Auto Capture ---
if "capture_threads" not in st.session_state:
    st.session_state.capture_threads = {} 

if "interfaces_started" not in st.session_state:
    st.session_state.interfaces_started = []  

# --- Background Continuous Capture Function ---
def continuous_capture(interface, device_id, packet_count):
    """
    Continuously captures packets on a given interface.
    Runs in a separate thread.
    """
    while True:
        try:
            start_packet_capture(interface, device_id, packet_count)
        except Exception as e:
            st.error(f"Error capturing on {interface}: {e}")
        time.sleep(1)  

# --- Main Monitoring Function ---

def network_monitoring():
    if "initialized" not in st.session_state:
         st.session_state["initialized"] = True

    if "capture_threads" not in st.session_state:
        st.session_state["capture_threads"] = {}
    if "interfaces_started" not in st.session_state:
        st.session_state["interfaces_started"] = []

    init_db()

    st.title("Network Monitoring")
    st.write("Real-time network monitoring and analysis.")

    device_identifier = get_mac_address()
    device_id = register_device(device_identifier, name="Monitored Device", device_type="real")

    
    with st.expander("⚙️ Monitoring Settings", expanded=False):
        available_interfaces = get_if_list()
        if not available_interfaces:
            st.error("No network interfaces found!")
            return
        
        selected_interfaces = st.multiselect("Select Network Interfaces", options=available_interfaces, default=available_interfaces)
        packet_count = st.number_input("Packets per Capture Cycle", min_value=1, max_value=100, value=10, step=1)

    if selected_interfaces:
        for iface in selected_interfaces:
            if iface not in st.session_state.interfaces_started:
                # Start a background thread for continuous capture on this interface
                thread = threading.Thread(target=continuous_capture, args=(iface, device_id, int(packet_count)), daemon=True)
                thread.start()
                st.session_state.capture_threads[iface] = thread
                st.session_state.interfaces_started.append(iface)


    st_autorefresh(interval=5000, key="network_autorefresh")
    
    logs = get_network_logs(device_id, limit=500)
    if logs:
        df_logs = pd.DataFrame(logs)
    else:
        df_logs = pd.DataFrame()


    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Data Usage per Website")
        if not df_logs.empty:
            df_web = df_logs.groupby("website", as_index=False)["data_usage"].sum()
            fig_web = px.pie(df_web, names="website", values="data_usage",
                             title="Data Usage Distribution by Website")
            st.plotly_chart(fig_web, use_container_width=True)
        else:
            st.info("No data available for website usage.")
    
    with col2:
        st.subheader("🔝 Top Source IPs by Data Usage")
        if not df_logs.empty:
            df_ips = df_logs.groupby("device_ip", as_index=False)["data_usage"].sum().sort_values(by="data_usage", ascending=False)
            fig_ips = px.bar(df_ips.head(5), x="device_ip", y="data_usage",
                             labels={"device_ip": "Source IP", "data_usage": "Data Usage (bytes)"},
                             title="Top 5 Source IPs")
            st.plotly_chart(fig_ips, use_container_width=True)
        else:
            st.info("No data available for source IP statistics.")
    
    # --- Traffic Analysis (Clustering) ---
    with st.expander("📈 Traffic Analysis", expanded=True):
        df_analysis = analyze_network_traffic(device_id, limit=100)
        if df_analysis.empty:
            st.info("Not enough data for analysis.")
        else:
            st.dataframe(df_analysis)
            fig_cluster = px.scatter(
                df_analysis,
                x="data_usage",
                y="duration",
                color="cluster",
                hover_data=["id", "device_ip", "website", "start_time"],
                title="Data Usage vs Duration Clustering"
            )
            st.plotly_chart(fig_cluster, use_container_width=True)

if __name__ == "__main__":
    network_monitoring()


