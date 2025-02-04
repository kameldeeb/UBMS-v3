# File: app/services/network_service.py
import psutil
import time

active_sessions = {}

def get_website_usage_data(tracked_websites):
    data = []
    connections = psutil.net_connections(kind='inet')

    for conn in connections:
        if conn.raddr and conn.status == psutil.CONN_ESTABLISHED:
            remote_ip = conn.raddr.ip
            remote_port = conn.raddr.port
            website = resolve_ip_to_domain(remote_ip)  # تحتاج دالة لتحويل IP إلى اسم نطاق

            if website in tracked_websites:
                session_key = f"{website}-{conn.pid}"

                if session_key not in active_sessions:
                    active_sessions[session_key] = {
                        "start_time": time.time(),
                        "data_used": 0
                    }

                # حساب مدة الاتصال
                duration = (time.time() - active_sessions[session_key]["start_time"]) / 60

                # حساب حجم البيانات (تحتاج بيانات من `psutil.net_io_counters()` مع تصفية على PID)
                data_used = active_sessions[session_key]["data_used"]

                data.append([website, round(duration, 2), round(data_used / (1024 * 1024), 2), time.strftime('%Y-%m-%d %H:%M:%S')])

    return data

def resolve_ip_to_domain(ip):
    # هذه الدالة تحتاج إلى استعلام DNS لتحويل IP إلى اسم نطاق
    import socket
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror:
        return ip  # في حال الفشل، نُعيد الـ IP نفسه
