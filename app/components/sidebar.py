# app/components/sidebar.py
import streamlit as st

def sidebar_navigation():
    st.sidebar.markdown("""
    <style>
    .sidebar .sidebar-content {
        background-image: linear-gradient(#2e7bcf,#2e7bcf);
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.sidebar.title("🚨 Threat Dashboard")
    return st.sidebar.radio("Navigation", [
        "📊 Real-time Monitoring",
        "🖥️ Device Management",
        "🚨 Alert System",
        "📈 Anomaly Analysis",
        "👤 User Profile"
    ])