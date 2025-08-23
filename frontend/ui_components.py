# /frontend/ui_components.py (Nayi File)

import streamlit as st
from streamlit_local_storage import LocalStorage

def apply_styles():
    """Poore app ke liye global styling aur double-sidebar fix apply karta hai."""
    st.markdown("""
        <style>
            /* Global Font and Button Styling */
            html, body, [class*="st-"], .st-emotion-cache-1avcm0n {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
            }
            .stButton > button {
                border-radius: 10px !important; font-weight: bold !important;
                transition: all 0.2s ease-in-out !important; border: 2px solid #0068C9 !important;
            }
            .stButton > button:hover {
                transform: scale(1.02); background-color: #0068C9 !important; color: white !important;
            }

            /* Double Sidebar Fix: Streamlit ke default navigation ko hamesha ke liye chupa dein */
            [data-testid="stSidebarNav"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)

def build_sidebar():
    """Har page par dikhne wala custom sidebar banata hai."""
    with st.sidebar:
        st.title("Health Companion")
        st.markdown(f"Welcome, \n**{st.session_state.get('user_email', 'User')}**!")
        st.markdown("---")
        
        st.page_link("streamlit_app.py", label=" Home", icon="🏠")
        st.page_link("pages/Dashboard.py", label=" Dashboard", icon="📈")
        st.page_link("pages/Medications.py", label=" Medications", icon="💊")
        st.page_link("pages/Appointments.py", label=" Appointments", icon="🗓️")
        st.page_link("pages/Contacts.py", label=" Contacts", icon="🆘")
        st.page_link("pages/Settings.py", label="⚙ Settings", icon="⚙️")
        
        st.markdown("---")
        if st.button("Logout", use_container_width=True):
            localS = LocalStorage()
            localS.deleteItem("access_token", key="storage_access_token_del")
            localS.deleteItem("user_email", key="storage_user_email_del")
            st.session_state.clear()
            st.toast("Logged out successfully.")
            st.switch_page("streamlit_app.py")
