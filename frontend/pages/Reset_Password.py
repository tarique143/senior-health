# frontend/pages/Reset_Password.py (Nayi File)

import streamlit as st
import requests
import os

# --- CONFIGURATION & API CLIENT ---
st.set_page_config(page_title="Reset Password", layout="centered", initial_sidebar_state="collapsed")
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

class ApiClient:
    def __init__(self, base_url): self.base_url = base_url
    def post(self, endpoint, json=None):
        try:
            return requests.post(f"{self.base_url}{endpoint}", json=json, timeout=10)
        except requests.exceptions.RequestException:
            st.error("Connection Error: Could not connect to the backend server."); return None

api = ApiClient(API_BASE_URL)

# --- HIDE SIDEBAR & CENTER CONTENT ---
st.markdown("""
    <style>
        section[data-testid="stSidebar"] { display: none; }
        .st-emotion-cache-1y4p8pa {
            display: flex; flex-direction: column;
            justify-content: center; align-items: center;
            height: 90vh;
        }
    </style>
""", unsafe_allow_html=True)


# --- PAGE LOGIC ---
st.title("🔑 Set Your New Password")

# URL se token nikaalein (e.g., ?token=xyz)
query_params = st.query_params
token = query_params.get("token")

if not token:
    st.error("Invalid password reset link. The token is missing. Please request a new link.")
    st.page_link("streamlit_app.py", label="Back to Login", icon="👈")
else:
    with st.form("reset_password_form"):
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        submitted = st.form_submit_button("Reset Password", use_container_width=True)
        
        if submitted:
            if not new_password or not confirm_password:
                st.warning("Please fill in both fields.")
            elif new_password != confirm_password:
                st.error("Passwords do not match!")
            else:
                with st.spinner("Updating password..."):
                    response = api.post(
                        "/users/reset-password",
                        json={"token": token, "new_password": new_password}
                    )
                
                if response and response.status_code == 200:
                    # Ek flag set karein taaki login page par success message dikhe
                    st.session_state['password_reset_success'] = True
                    # User ko login page par redirect karein
                    st.switch_page("streamlit_app.py")
                else:
                    error_detail = "Invalid or expired token. Please request a new reset link."
                    if response:
                        try:
                            error_detail = response.json().get('detail', error_detail)
                        except:
                            pass # Use default error
                    st.error(f"Failed to reset password: {error_detail}")
