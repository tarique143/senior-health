# /frontend/ui_components.py

import streamlit as st
from streamlit_local_storage import LocalStorage

# Initialize the local storage client.
localS = LocalStorage()

def apply_styles():
    """
    Applies global CSS styles to the Streamlit application.
    This includes the fix to hide Streamlit's default page navigation,
    thus preventing the "double sidebar" issue.
    """
    st.markdown("""
        <style>
            /* --- Global Font and Layout Styling --- */
            html, body, [class*="st-"], .st-emotion-cache-1avcm0n {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
            }
            /* --- Custom Button Styling --- */
            .stButton > button {
                border-radius: 10px !important; font-weight: bold !important;
                transition: all 0.2s ease-in-out !important; border: 2px solid #0068C9 !important;
            }
            .stButton > button:hover {
                transform: scale(1.02); background-color: #0068C9 !important; color: white !important;
            }
            /* --- Emergency SOS Bar --- */
            .emergency-bar {
                display: block; width: 100%; background-color: #dc3545; color: white;
                text-align: center; padding: 10px; font-weight: bold; font-size: 1.1rem;
                text-decoration: none; border-radius: 5px; margin-bottom: 20px;
                transition: background-color 0.3s;
            }
            .emergency-bar:hover { background-color: #c82333; color: white; }
            /* --- FIX for Double Sidebar --- */
            [data-testid="stSidebarNav"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)


def build_sidebar():
    """
    Creates and displays the custom sidebar navigation menu for the application.
    """
    with st.sidebar:
        st.title("🏥 Health Companion")
        if st.session_state.get('user_email'):
            st.markdown(f"Welcome, \n**{st.session_state.get('user_email')}**!")
        st.markdown("---")

        # --- Navigation Links ---
        st.page_link("streamlit_app.py", label="Home", icon="🏠")
        st.page_link("pages/Dashboard.py", label="Dashboard", icon="📈")
        st.page_link("pages/Medications.py", label="Medications", icon="💊")
        st.page_link("pages/Appointments.py", label="Appointments", icon="🗓️")
        st.page_link("pages/Contacts.py", label="Emergency Contacts", icon="🆘")
        st.page_link("pages/Settings.py", label="Settings", icon="⚙️")
        st.markdown("---")

        # --- Logout Button ---
        if st.button("Logout", use_container_width=True):
            # Added unique keys for each deleteItem call
            localS.deleteItem("access_token", key="storage_access_token_del")
            localS.deleteItem("user_email", key="storage_user_email_del")
            st.session_state.clear()
            st.toast("Logged out successfully.")
            st.switch_page("streamlit_app.py")
