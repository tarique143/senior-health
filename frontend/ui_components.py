# /frontend/ui_components.py

import streamlit as st
from streamlit_local_storage import LocalStorage

# Initialize the local storage client.
localS = LocalStorage()

def apply_styles():
    """
    Applies global CSS styles to the Streamlit application.
    This includes custom fonts, button styles, the emergency bar,
    and a critical fix to hide Streamlit's default page navigation
    when using a custom sidebar.
    """
    st.markdown("""
        <style>
            /* --- Global Font and Layout Styling --- */
            html, body, [class*="st-"], .st-emotion-cache-1avcm0n {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
            }
            /* --- Custom Button Styling --- */
            .stButton > button {
                border-radius: 10px !important;
                font-weight: bold !important;
                transition: all 0.2s ease-in-out !important;
                border: 2px solid #0068C9 !important;
            }
            .stButton > button:hover {
                transform: scale(1.02);
                background-color: #0068C9 !important;
                color: white !important;
            }

            /* --- Emergency SOS Bar --- */
            .emergency-bar {
                display: block;
                width: 100%;
                background-color: #dc3545; /* Red color */
                color: white;
                text-align: center;
                padding: 10px;
                font-weight: bold;
                font-size: 1.1rem;
                text-decoration: none;
                border-radius: 5px;
                margin-bottom: 20px;
                transition: background-color 0.3s;
            }
            .emergency-bar:hover {
                background-color: #c82333; /* Darker red on hover */
                color: white;
            }

            /* --- CRITICAL FIX: Hide Streamlit's Default Sidebar Navigation --- */
            /* This prevents the "double sidebar" issue when building our own custom sidebar. */
            [data-testid="stSidebarNav"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)


def build_sidebar():
    """
    Creates and displays the custom sidebar navigation menu for the application.
    This function should be called on every page where the sidebar is needed.
    """
    with st.sidebar:
        st.title("🏥 Health Companion")
        if st.session_state.get('user_email'):
            st.markdown(f"Welcome, \n**{st.session_state.get('user_email')}**!")
        st.markdown("---")

        # --- Navigation Links ---
        # `st.page_link` is the modern way to create navigation in Streamlit.
        st.page_link("streamlit_app.py", label="Home", icon="🏠")
        st.page_link("pages/Dashboard.py", label="Dashboard", icon="📈")
        st.page_link("pages/Medications.py", label="Medications", icon="💊")
        st.page_link("pages/Appointments.py", label="Appointments", icon="🗓️")
        st.page_link("pages/Contacts.py", label="Emergency Contacts", icon="🆘")
        st.page_link("pages/Settings.py", label="Settings", icon="⚙️")

        st.markdown("---")
        st.info("This app is a tool to help you manage your health schedule.", icon="💡")
        st.markdown("---")

        # --- Logout Button ---
        if st.button("Logout", use_container_width=True):
            # 1. Clear the "Remember Me" token from browser's local storage.
            localS.deleteItem("access_token")
            localS.deleteItem("user_email")

            # 2. Clear all data from the current session state.
            st.session_state.clear()

            # 3. Show a confirmation message and redirect to the login page.
            st.toast("You have been logged out successfully.")
            st.switch_page("streamlit_app.py")
