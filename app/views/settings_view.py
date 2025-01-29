import streamlit as st


def system_settings():
    st.header("👤 User Configuration")
    
    with st.form("user_profile"):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Full Name", "Salman Alotaibi")
            st.selectbox("Role", ["Admin", "Operator", "Viewer"])
        with col2:
            st.text_input("Email", "Salman@aou.org")
            st.text_input("Phone", "+123456789")
        
        st.form_submit_button("Update Profile")