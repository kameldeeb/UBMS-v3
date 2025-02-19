# app/utils/logger.py
import json
import streamlit as st
from datetime import datetime

def log_alert(device_id, message, score):
    alert = {
        'time': datetime.now().isoformat(),
        'device_id': device_id,
        'message': message,
        'score': score
    }
    st.session_state.alerts.append(alert)
    
    # Save to file
    with open("data/alerts.log", "a") as f:
        f.write(json.dumps(alert) + "\n")