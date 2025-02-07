# File: app/services/network_service.py
import psutil
import time
import socket
from app.services.db_manager import log_network_log

active_sessions = {}

def get_website_usage_data(tracked_websites):

    data = []
    connections = psutil.net_connections(kind='inet')
    
    for conn in connections:
        if conn.raddr and conn.status == psutil.CONN_ESTABLISHED:
            remote_ip = conn.raddr.ip
            website = resolve_ip_to_domain(remote_ip)
            
            if website in tracked_websites:
                session_key = f"{website}-{conn.pid}"
                
                if session_key not in active_sessions:
                    active_sessions[session_key] = {
                        "start_time": time.time(),
                        "data_used": 0  
                    }
                
                duration = (time.time() - active_sessions[session_key]["start_time"]) / 60.0
                data_used = active_sessions[session_key]["data_used"]
                
                snapshot_time = time.strftime('%Y-%m-%d %H:%M:%S')
                
                data.append([website, round(duration, 2), round(data_used / (1024 * 1024), 2), snapshot_time])
    return data

def log_network_usage(device_id, tracked_websites):
    """
    For each record, the following fields are used:
      - device_id: provided as a parameter (from the unified device registration)
      - device_ip: left as None (adjust if you wish to log the device's IP)
      - website: the tracked website or domain
      - start_time: for this snapshot, we use the snapshot time (adjust as needed)
      - end_time: same as start_time (since we're taking a snapshot)
      - duration: duration in minutes that the session has been active
      - data_usage: data usage in MB
    """
    usage_data = get_website_usage_data(tracked_websites)
    
    for record in usage_data:
        website, duration, data_used, snapshot_time = record
        log_network_log(
            device_id=device_id,
            device_ip=None,  
            website=website,
            start_time=snapshot_time,
            end_time=snapshot_time,
            duration=duration,
            data_usage=data_used
        )

def resolve_ip_to_domain(ip):

    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror:
        return ip
