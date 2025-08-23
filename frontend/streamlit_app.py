# frontend/streamlit_app.py (Corrected Version 1)

import streamlit as st
import requests
import time
import os
from datetime import datetime

# --- CONFIGURATION & PAGE CONFIG ---
st.set_page_config(page_title="Health Companion", layout="wide", initial_sidebar_state="auto")

# --- BACKEND API URL ---
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# --- API CLIENT CLASS ---
class ApiClient:
    def __init__(self, base_url): self.base_url = base_url
    def _get_headers(self):
        token = st.session_state.get("access_token") ### <<< CHANGE HERE
        if not token:
            return {}
        return {"Authorization": f"Bearer {token}"}
    def _make_request(self, method, endpoint, **kwargs):
        # Redirect to login if token is missing
        ### <<< CHANGE HERE (and in the check below)
        if "access_token" not in st.session_state and endpoint not in ["/users/token", "/users/register", "/users/forgot-password", "/users/reset-password"]:
            # Don't switch page here, let the main controller handle it
            pass
        try:
            return requests.request(method, f"{self.base_url}{endpoint}", headers=self._get_headers(), timeout=10, **kwargs)
        except requests.exceptions.RequestException:
            st.error("Connection Error: Could not connect to the backend server."); return None
    def get(self, endpoint, params=None): return self._make_request("GET", endpoint, params=params)
    def post(self, endpoint, data=None, json=None): return self._make_request("POST", endpoint, data=data, json=json)

api = ApiClient(API_BASE_URL)

# --- STYLING FUNCTIONS ---
def apply_global_styles():
    st.markdown("""
        <style>
            html, body, [class*="st-"], .st-emotion-cache-1avcm0n {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .stButton > button {
                border-radius: 10px !important;
                font-weight: bold !important;
            }
        </style>
    """, unsafe_allow_html=True)

def apply_themed_styles():
    # ... (Your existing themed styling here) ...
    st.markdown("""
        <style>
        .nav-card {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            transition: all 0.3s ease-in-out;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            height: 100%;
        }
        .nav-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.1);
            border-color: #0068C9;
        }
        /* ... other styles ... */
        </style>
    """, unsafe_allow_html=True)


# --- HEADER COMPONENT ---
def create_header():
    current_time = time.strftime("%I:%M:%S %p")
    current_date = time.strftime("%A, %B %d, %Y")
    st.markdown(f"""
        <div style="text-align: right; margin-bottom: 2rem;">
            <h2 style="margin: 0; font-weight: 600;">{current_time}</h2>
            <p style="margin: 0; color: #555;">{current_date}</p>
        </div>
    """, unsafe_allow_html=True)


# --- AUTHENTICATION PAGE FUNCTION ---
def show_login_register_page():
    st.markdown('<div style="text-align:center;"><h1>Welcome to Health Companion</h1></div>', unsafe_allow_html=True)
    
    # Check for password reset success message
    if st.session_state.pop('password_reset_success', False):
        st.success("Your password has been reset successfully! Please log in with your new password.")

    login_tab, register_tab = st.tabs(["**Login**", "**Register**"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            login_submitted = st.form_submit_button("Login", use_container_width=True, type="primary")

            if login_submitted:
                with st.spinner("Logging in..."):
                    response = api.post("/users/token", data={"username": email, "password": password})
                
                if response and response.status_code == 200:
                    ### <<< CHANGE HERE: Save 'access_token', not 'token'
                    st.session_state['access_token'] = response.json().get("access_token")
                    st.session_state['user_email'] = email
                    st.toast("Login successful!", icon="🎉")
                    st.rerun()
                else:
                    st.error("Incorrect email or password.")
        
        # Forgot Password Logic
        if st.button("Forgot Password?", key="forgot_pass_btn"):
            st.session_state.show_forgot_password = True
        
        if st.session_state.get('show_forgot_password'):
            with st.form("forgot_password_form", clear_on_submit=True):
                st.subheader("Reset Your Password")
                forgot_email = st.text_input("Enter your registered email")
                if st.form_submit_button("Send Reset Link"):
                    with st.spinner("Sending..."):
                        response = api.post("/users/forgot-password", json={"email": forgot_email})
                    st.success("If an account with that email exists, a reset link has been sent.")
                    st.session_state.show_forgot_password = False # Hide form after submission
                    st.rerun()

    with register_tab:
        with st.form("register_form", clear_on_submit=True):
            full_name = st.text_input("Full Name")
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            register_submitted = st.form_submit_button("Register", use_container_width=True)

            if register_submitted:
                with st.spinner("Creating account..."):
                    response = api.post("/users/register", json={"full_name": full_name, "email": reg_email, "password": reg_password})
                if response and response.status_code == 201:
                    st.success("Account created successfully! Please login.")
                else:
                    error = "Failed to register. Email may already be in use."
                    st.error(error)

### --- MAIN APP AREA FUNCTION --- ###
def show_main_app_area():
    st.title(f"Welcome to your Health Companion, {st.session_state.get('user_email', 'User').split('@')[0]}!")
    st.markdown("This is your central hub. From here, you can manage all aspects of your health schedule.")
    st.markdown("---")

    # Fetch quick stats
    with st.spinner("Loading today's summary..."):
        meds_response = api.get("/medications/")
        apps_response = api.get("/appointments/")

    active_meds_count = 0
    if meds_response and meds_response.status_code == 200:
        active_meds_count = sum(1 for med in meds_response.json() if med['is_active'])

    today_apps_count = 0
    if apps_response and apps_response.status_code == 200:
        today = datetime.now().date()
        today_apps_count = sum(1 for app in apps_response.json() if datetime.fromisoformat(app['appointment_datetime']).date() == today)
    
    # Quick Stats Display
    st.subheader("Today's at a Glance")
    # ... (rest of this function is OK) ...
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Active Medications", value=f"{active_meds_count} meds")
    with col2:
        st.metric(label="Appointments Today", value=f"{today_apps_count} visits")
    with col3:
        st.metric(label="Health Tip", value="Ready!", help="A new tip is waiting for you on the dashboard!")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Navigation Cards
    st.subheader("What would you like to do?")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="nav-card"><div class="icon">📈</div><h3>Go to Dashboard</h3><p>View your complete daily schedule and health tips.</p></div>', unsafe_allow_html=True)
        if st.button("Open Dashboard", use_container_width=True, key="dash_btn"):
            st.switch_page("pages/Dashboard.py")
    with col2:
        st.markdown('<div class="nav-card"><div class="icon">💊</div><h3>Manage Medications</h3><p>Add, edit, or view your medication list and schedule.</p></div>', unsafe_allow_html=True)
        if st.button("Manage Meds", use_container_width=True, key="med_btn"):
            st.switch_page("pages/Medications.py")
    with col3:
        st.markdown('<div class="nav-card"><div class="icon">🗓️</div><h3>Manage Appointments</h3><p>Keep track of all your upcoming doctor visits.</p></div>', unsafe_allow_html=True)
        if st.button("Manage Appointments", use_container_width=True, key="app_btn"):
            st.switch_page("pages/Appointments.py")
    with col4:
        st.markdown('<div class="nav-card"><div class="icon">⚙️</div><h3>My Settings</h3><p>Update your profile, password, and contacts.</p></div>', unsafe_allow_html=True)
        if st.button("Go to Settings", use_container_width=True, key="set_btn"):
            st.switch_page("pages/Settings.py")


### --- MAIN APPLICATION CONTROLLER (UPDATED) --- ###
def main():
    apply_global_styles()

    ### <<< CHANGE HERE
    if "access_token" not in st.session_state:
        show_login_register_page() 
    else:
        apply_themed_styles()

        st.sidebar.title("Navigation")
        st.sidebar.markdown(f"Welcome, \n**{st.session_state.get('user_email', 'User')}**!")
        if st.sidebar.button("Logout", use_container_width=True):
            st.session_state.clear(); st.toast("Logged out successfully."); st.rerun()
        
        create_header()
        show_main_app_area()

if __name__ == "__main__":
    main()
