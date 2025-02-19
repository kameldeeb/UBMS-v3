# File: app/services/network_service.py

from scapy.all import sniff
from datetime import datetime
import pandas as pd
from sklearn.cluster import KMeans
from app.services.db_manager import log_network_log, get_network_logs

def packet_callback(packet, device_id):

    if packet.haslayer("IP"):
        device_ip = packet["IP"].src
        website = packet["IP"].dst 
        start_time = datetime.now().isoformat()
        end_time = start_time 
        duration = 0.0
        data_usage = float(len(packet)) 
        log_network_log(device_id, device_ip, website, start_time, end_time, duration, data_usage)

def start_packet_capture(interface, device_id, packet_count=10):

    sniff(prn=lambda pkt: packet_callback(pkt, device_id),
          iface=interface,
          count=packet_count,
          store=False)

def analyze_network_traffic(device_id, limit=100):

    logs = get_network_logs(device_id, limit=limit)
    if not logs:
        return pd.DataFrame()

    df = pd.DataFrame(logs)
    df['data_usage'] = pd.to_numeric(df['data_usage'], errors='coerce')
    df['duration'] = pd.to_numeric(df['duration'], errors='coerce')
    df.dropna(subset=['data_usage', 'duration'], inplace=True)
    
    if len(df) < 2:
        df['cluster'] = 0
        return df

    X = df[['data_usage', 'duration']]
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10) 

    df['cluster'] = kmeans.fit_predict(X)
    return df



