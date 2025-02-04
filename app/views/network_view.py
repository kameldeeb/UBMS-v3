# app/views/network_view.py
import streamlit as st
import netifaces
from scapy.all import AsyncSniffer, IP, TCP, DNS, UDP, sniff
from scapy.packet import Packet
from collections import defaultdict
import time
from datetime import datetime
import threading
import pandas as pd
import plotly.express as px
from queue import Queue, Empty

# ----------- Constants & Configurations -----------
COMMON_PORTS = {
    80: "HTTP", 443: "HTTPS", 21: "FTP", 
    22: "SSH", 53: "DNS", 25: "SMTP"
}

THREAT_INTEL_FEEDS = {
    "malicious_ips": {"192.168.1.666", "10.0.0.99"},
    "suspicious_domains": ["malware.com", "phishing.net"]
}

# ----------- Session State Initialization -----------
def init_session_state():
    defaults = {
        'packets': [],
        'alerts': [],
        'is_sniffing': False,
        'packet_queue': Queue(),
        'traffic_stats': defaultdict(int),
        'selected_interfaces': [],
        'ip_filters': [],
        'anomaly_rules': {
            'port_scan_threshold': 5,
            'data_threshold': 10000,
            'dns_monitoring': True
        }
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

# ----------- Dynamic Configuration UI -----------
def show_configuration_panel():
    with st.sidebar.expander("⚙️ Monitoring Settings"):
        # Interface Selection
        interfaces = netifaces.interfaces()
        st.session_state.selected_interfaces = st.multiselect(
            "Network Interfaces",
            interfaces,
            default=interfaces[:1]
        )
        
        # IP Filtering
        st.session_state.ip_filters = st.text_area(
            "IP Filters (comma-separated):",
            "192.168.1.1, 10.0.0.0/24"
        ).split(',')
        
        # Anomaly Rules
        st.session_state.anomaly_rules['port_scan_threshold'] = st.slider(
            "Port Scan Threshold (SYN/min)",
            1, 20, 5
        )
        st.session_state.anomaly_rules['data_threshold'] = st.number_input(
            "Data Transfer Alert Threshold (KB)",
            100, 10000, 5000
        ) * 1024  # Convert to bytes

# ----------- Packet Processing & Anomaly Detection -----------
def process_packet(packet: Packet):
    if IP not in packet:
        return

    # Apply IP Filters
    src_ip = packet[IP].src
    dst_ip = packet[IP].dst
    if any(filt in src_ip or filt in dst_ip for filt in st.session_state.ip_filters):
        return

    # Basic Packet Info
    pkt_info = {
        'timestamp': packet.time,
        'time': datetime.fromtimestamp(packet.time).strftime('%H:%M:%S'),
        'src': src_ip,
        'dst': dst_ip,
        'proto': packet.sprintf("%IP.proto%"),
        'length': len(packet),
        'flags': '',
        'dport': '',
        'dns_query': ''
    }

    # TCP Analysis
    if TCP in packet:
        pkt_info.update({
            'dport': packet[TCP].dport,
            'flags': packet.sprintf("%TCP.flags%")
        })
        check_port_scan(pkt_info)

    # DNS Analysis
    if DNS in packet and packet[DNS].qr == 0:
        try:
            query = packet[DNS].qd.qname.decode('utf-8').rstrip('.')
            pkt_info['dns_query'] = query
            check_dns_threats(query)
        except:
            pass

    # Data Transfer Monitoring
    if packet[IP].src.startswith('192.168'):
        st.session_state.traffic_stats['internal_out'] += len(packet)
    else:
        st.session_state.traffic_stats['external_in'] += len(packet)

    st.session_state.packet_queue.put(pkt_info)

def check_port_scan(pkt):
    if 'S' in pkt['flags']:  # SYN Scan Detection
        key = f"syn_{pkt['src']}"
        st.session_state.traffic_stats[key] += 1
        
        if st.session_state.traffic_stats[key] > st.session_state.anomaly_rules['port_scan_threshold']:
            alert = f"🚨 Port Scan Detected from {pkt['src']} ({st.session_state.traffic_stats[key]} SYN attempts)"
            if alert not in st.session_state.alerts:
                st.session_state.alerts.append(alert)

def check_dns_threats(query):
    for domain in THREAT_INTEL_FEEDS['suspicious_domains']:
        if domain in query:
            st.session_state.alerts.append(f"🚨 Suspicious DNS Query: {query}")

# ----------- Real-time Visualizations -----------
def show_traffic_dashboard():
    col1, col2, col3 = st.columns(3)
    
    # Traffic Distribution
    with col1:
        st.subheader("🌐 Traffic Flow")
        traffic_data = {
            'Direction': ['Internal Out', 'External In'],
            'Bytes': [
                st.session_state.traffic_stats['internal_out'],
                st.session_state.traffic_stats['external_in']
            ]
        }
        fig = px.pie(traffic_data, names='Direction', values='Bytes')
        st.plotly_chart(fig, use_container_width=True)
    
    # Protocol Distribution
    with col2:
        st.subheader("📊 Protocols")
        proto_counts = defaultdict(int)
        for pkt in st.session_state.packets:
            proto_counts[pkt['proto']] += 1
        # Create DataFrame for protocol counts
        proto_df = pd.DataFrame({
            'Protocol': list(proto_counts.keys()),
            'Count': list(proto_counts.values())
        })

        # Plot bar chart using the DataFrame
        fig = px.bar(proto_df, x='Protocol', y='Count', labels={'x': 'Protocol', 'y': 'Count'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Top Talkers
    with col3:
        st.subheader("🔝 Top Talkers")
        talkers = defaultdict(int)
        for pkt in st.session_state.packets:
            talkers[pkt['src']] += pkt['length']
        df = pd.DataFrame(sorted(talkers.items(), key=lambda x: -x[1])[:5], columns=['IP', 'Bytes'])
        st.dataframe(df.style.highlight_max(axis=0), use_container_width=True)

# ----------- Main UI Components -----------
def network_monitoring():
    st.title("🌐 Advanced Network Monitoring")
    init_session_state()
    show_configuration_panel()
    
    # Control Panel
    with st.container():
        col1, col2, col3 = st.columns([2,1,1])
        with col1:
            if st.button("▶️ Start Capture" if not st.session_state.is_sniffing else "⏹️ Stop Capture"):
                toggle_sniffing()
        
        with col2:
            if st.button("🔄 Clear Alerts"):
                st.session_state.alerts.clear()
        
        with col3:
            st.caption(f"📦 Packet Buffer: {len(st.session_state.packets)}")

    # Real-time Alerts
    if st.session_state.alerts:
        with st.expander("🚨 Active Alerts (Last 10)", expanded=True):
            for alert in list(st.session_state.alerts)[-10:]:
                st.error(alert, icon="⚠️")

    # Traffic Dashboard
    show_traffic_dashboard()
    
    # Packet Stream Display
    with st.expander("📜 Live Packet Stream", expanded=True):
        display_packet_table()

    # Background Sniffer Management
    manage_sniffer()

# ----------- Helper Functions -----------
def toggle_sniffing():
    st.session_state.is_sniffing = not st.session_state.is_sniffing

def manage_sniffer():
    if st.session_state.is_sniffing and 'sniffer' not in st.session_state:
        st.session_state.sniffer = AsyncSniffer(
            iface=st.session_state.selected_interfaces,
            prn=process_packet,
            store=False
        )
        st.session_state.sniffer.start()
    elif not st.session_state.is_sniffing and 'sniffer' in st.session_state:
        st.session_state.sniffer.stop()
        del st.session_state.sniffer

def display_packet_table():
    try:
        while True:
            pkt = st.session_state.packet_queue.get_nowait()
            detect_advanced_anomalies(pkt)
            st.session_state.packets.insert(0, pkt)
            if len(st.session_state.packets) > 200:
                st.session_state.packets.pop()
    except Empty:
        pass

    if st.session_state.packets:
        df = pd.DataFrame(st.session_state.packets[:50])
        df['service'] = df['dport'].apply(lambda x: COMMON_PORTS.get(x, 'Other'))
        st.dataframe(
            df[['time', 'src', 'dst', 'proto', 'service', 'length']],
            column_config={
                "time": "Timestamp",
                "src": "Source",
                "dst": "Destination",
                "proto": "Protocol",
                "service": "Service",
                "length": {"header": "Size (bytes)", "format": "📦 %d"}
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No packets captured. Start the capture to monitor traffic.")

def detect_advanced_anomalies(pkt):
    # Large Data Transfer Detection
    if pkt['length'] > st.session_state.anomaly_rules['data_threshold']:
        alert = f"🔔 Large Data Transfer: {pkt['src']} → {pkt['dst']} ({pkt['length']//1024} KB)"
        if alert not in st.session_state.alerts:
            st.session_state.alerts.append(alert)
    
    # Known Malicious IP Detection
    if pkt['src'] in THREAT_INTEL_FEEDS['malicious_ips']:
        st.session_state.alerts.append(f"⛔ Known Malicious IP: {pkt['src']}")

# ----------- Run the Module -----------
if __name__ == "__main__":
    network_monitoring()