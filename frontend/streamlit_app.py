# frontend/streamlit_app.py (The Main App & Login Gatekeeper)

import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURATION ---
# This remains here as it's part of the login logic
API_BASE_URL = "http://127.0.0.1:8000"


# --- API CLIENT CLASS ---
# This class is needed here for the login/register API calls
class ApiClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = st.session_state.get("token", None)

    def _get_headers(self):
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

    def _make_request(self, method, endpoint, **kwargs):
        """A robust request handler to prevent crashes from connection errors."""
        try:
            response = requests.request(method, f"{self.base_url}{endpoint}", headers=self._get_headers(), **kwargs)
            return response
        except requests.exceptions.ConnectionError:
            st.error("Connection Error: Could not connect to the backend server. Please ensure it is running.")
            return None

    def post(self, endpoint, data=None, json=None):
        return self._make_request("POST", endpoint, data=data, json=json)

api = ApiClient(API_BASE_URL)


# --- STYLING AND PAGE CONFIG ---
st.set_page_config(
    page_title="Health Companion",
    layout="wide",
    initial_sidebar_state="collapsed" # Sidebar will be collapsed on login page
)

def set_page_style():
    """Injects custom CSS for a mobile-responsive and accessible UI."""
    st.markdown("""
        <style>
            html, body, [class*="st-"] { font-size: 18px; }
            .stButton>button {
                background-color: #0068c9; color: white; border-radius: 8px;
                padding: 12px 28px; border: none; font-weight: bold; width: 100%;
            }
            .stButton>button:hover { background-color: #0055a3; }
        </style>
    """, unsafe_allow_html=True)


# --- AUTHENTICATION PAGE FUNCTION ---
def show_login_register_page():
    """Displays the login and registration forms for unauthenticated users."""
    st.title("Welcome to Your Health Companion!")
    st.write("Your personal assistant for managing health and well-being.")

    # Show a message if the user just registered, guiding them to log in
    if st.session_state.get('just_registered', False):
        st.success("Registration successful! Please login with your new account.")
        del st.session_state['just_registered'] # Clear the flag so it doesn't show again

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                response = api.post("/users/token", data={"username": email, "password": password})
                if response and response.status_code == 200:
                    st.session_state["token"] = response.json()["access_token"]
                    st.session_state["user_email"] = email
                    st.toast("Login Successful!", icon="🎉")
                    st.rerun() # Rerun the app to move past the login gate
                else:
                    st.error("Login Failed: Incorrect credentials or server is down.")

    with register_tab:
        with st.form("register_form"):
            full_name = st.text_input("Full Name")
            new_email = st.text_input("New Email")
            new_password = st.text_input("New Password", type="password")
            if st.form_submit_button("Register"):
                response = api.post("/users/register", json={"full_name": full_name, "email": new_email, "password": new_password})
                if response and response.status_code == 201:
                    # Set a flag and rerun to show the success message on the login page
                    st.session_state['just_registered'] = True
                    st.rerun()
                else:
                    st.error("Registration Failed: Email may already exist or server is down.")


# --- MAIN APPLICATION CONTROLLER ---
def main():
    """
    This is the main "gatekeeper" of the application.
    It decides whether to show the login page or the main app with its sidebar.
    """
    set_page_style()

    # If user is not logged in, show the login/register page
    if "token" not in st.session_state:
        show_login_register_page()
    else:
        # If user IS logged in, configure the sidebar and let Streamlit's
        # multi-page navigation handle the rest.
        st.sidebar.title("Health Companion")
        st.sidebar.write(f"Welcome, {st.session_state.get('user_email', 'User')}!")
        
        if st.sidebar.button("Logout"):
            st.session_state.clear()
            st.toast("Logged out successfully.")
            st.rerun()
        
        # When logged in, show a welcome message on the main page.
        # The actual pages (Dashboard, etc.) are in the 'pages' folder.
        st.title("Welcome!")
        st.write("Please select a page from the sidebar to manage your health information.")
        st.info("Your other pages like Dashboard, Medications, etc., are listed in the sidebar. Click on them to navigate.", icon="👈")


if __name__ == "__main__":
    main()