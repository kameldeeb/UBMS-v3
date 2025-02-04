import streamlit as st
from streamlit_option_menu import option_menu

def sidebar_navigation():
    with st.sidebar:
        # Add a logo or an icon at the top
        # st.markdown("""
        # <div style="text-align: center; margin-bottom: 20px;">
        #     <h3 style="color: white;">UBMS Dashboard</h3>
        # </div>
        # """, unsafe_allow_html=True)

        # Create the menu
        selected = option_menu(
            menu_title=None,
        options = [
            "Dashboard",
            "Anomaly Analysis",
            "---",                
            "Device Management", 
            "Alert System",
            "---",
            "File Monitoring", 
            "USB Monitoring",
            "Login Monitoring",
            "Network Monitoring",
            "Process Monitoring",
            "---", 
            # "User Profile", 
            "System Settings"
        ],

        icons = [
            "house",          # Overview
            "graph-up",          # Anomaly Analysis
            None,  
            "laptop",              # Device Management
            "bell",                # Alert System
            None,  
            "file-earmark-text",   # File Monitoring
            "usb-drive",           # USB Monitoring
            "shield-lock",         # Login Monitoring
            "wifi",                # Network Monitor
            "cpu",               # Process Monitor
            None,  
            # "person-circle",       # User Profile
            "gear"                 # System Settings
            ],

            menu_icon="menu-up",
            default_index=0,
            orientation="vertical",
            styles={
                "container": {"padding": "5px", "background-color": "rgba(0,0,0,0.1)"},
                "nav-link": {
                    "font-size": "16px",
                    "font-weight": "bold",
                    "color": "white",
                    "text-align": "left",
                    "margin": "5px",
                    "border-radius": "8px",
                    "padding": "12px",
                },
            }
        )


        return selected
