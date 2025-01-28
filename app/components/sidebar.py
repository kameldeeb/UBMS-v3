import streamlit as st
from streamlit_option_menu import option_menu

def sidebar_navigation():
    with st.sidebar:
        # Add a logo or an icon at the top
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h3 style="color: white;">UBMS Dashboard</h3>
        </div>
        """, unsafe_allow_html=True)

        # Create the menu
        selected = option_menu(
            menu_title=None,
            options=[
                "Real-time Monitoring", 
                "Device Management", 
                "Alert System",
                "---",
                "Anomaly Analysis", 
                "User Profile", 
                "---",
                "System Settings"
            ],
            icons=[
                "graph-up", 
                "laptop", 
                "bell",
                None,  
                "bar-chart", 
                "person", 
                None,  
                "gear"
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

        # Add copyright/author name at the bottom
        st.markdown("""
        <div style="position: fixed; bottom: 20px; left: 10px; width: 100%; text-align: left; color: white; font-size: 12px;">
            © 2025 All rights reserved.
        </div>
        """, unsafe_allow_html=True)

        return selected
