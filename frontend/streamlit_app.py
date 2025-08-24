# /frontend/streamlit_app.py

# --- 1. SABSE ZAROORI FIX (THE MOST IMPORTANT FIX) ---
# YEH NAYA CODE HAI JO IMPORT ERROR KO HAMESHA KE LIYE THEEK KAREGA
import sys
import os

# Is file (streamlit_app.py) ka poora path lo, uske folder (frontend) ka path nikalo,
# aur us folder ko Python ke search path mein daal do.
# Ab Python ko hamesha ui_components.py mil jaayega.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- 2. STANDARD & THIRD-PARTY IMPORTS ---
import random
import time
from datetime import date, datetime

import pytz
import requests
import streamlit as st
from streamlit_local_storage import LocalStorage

# --- 3. PAGE CONFIGURATION ---
# Yeh ab bilkul sahi jagah par hai.
st.set_page_config(
    page_title="Health Companion",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🏠"
)

# --- 4. LOCAL IMPORTS (AB YEH 100% KAAM KAREGA) ---
# Upar diye gaye fix ke kaaran, ab yeh import kabhi fail nahi hoga.
from ui_components import apply_styles, build_sidebar

# --- 5. GLOBAL VARIABLES & CONSTANTS ---
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
localS = LocalStorage()

# --- 6. EXECUTION OF INITIAL UI SETUP ---
apply_styles()


# --- 7. API CLIENT CLASS ---
class ApiClient:
    """A client to interact with the backend API."""
    def __init__(self, base_url: str):
        self.base_url = base_url

    def _get_headers(self) -> dict:
        token = st.session_state.get("access_token")
        return {"Authorization": f"Bearer {token}"} if token else {}

    def _make_request(self, method: str, endpoint: str, **kwargs):
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method, url, headers=self._get_headers(), timeout=15, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401: return None
            st.error(f"API Error: {e.response.json().get('detail', 'Unknown error')}")
        except requests.exceptions.RequestException:
            st.error("Connection Error: Could not connect to the backend server.")
        return None

    def get(self, endpoint: str): return self._make_request("GET", endpoint)
    def post(self, endpoint: str, data=None, json=None): return self._make_request("POST", endpoint, data=data, json=json)

api = ApiClient(API_BASE_URL)


# --- 8. UI HELPER FUNCTIONS ---
def create_header():
    """Displays the current time and date in IST."""
    now_ist = datetime.now(pytz.timezone("Asia/Kolkata"))
    st.markdown(f"""
        <div style="text-align: right; margin-bottom: 2rem;">
            <h2 style="margin: 0; font-weight: 600;">{now_ist.strftime("%I:%M:%S %p")}</h2>
            <p style="margin: 0; color: #555;">{now_ist.strftime("%A, %B %d, %Y")}</p>
        </div>
    """, unsafe_allow_html=True)

def create_sos_bar():
    """Displays an emergency SOS bar."""
    response = api.get("/contacts/")
    emergency_contact = response.json()[0] if response and response.status_code == 200 and response.json() else None
    if emergency_contact:
        st.markdown(f'<a href="tel:{emergency_contact["phone_number"]}" class="emergency-bar" target="_blank">🚨 EMERGENCY SOS (Call {emergency_contact["name"]}) 🚨</a>', unsafe_allow_html=True)
    else:
        st.markdown('<a href="/Contacts" class="emergency-bar" target="_self">⚠️ Set Up Your Primary SOS Contact ⚠️</a>', unsafe_allow_html=True)


# --- 9. PAGE RENDERING LOGIC ---
def show_login_register_page():
    """Displays the forms for login, registration, and password reset."""
    st.markdown('<div style="text-align:center;"><h1>Welcome to Health Companion</h1></div>', unsafe_allow_html=True)
    
    if st.session_state.pop('password_reset_success', False):
        st.success("Your password has been reset successfully! Please log in.")

    login_tab, register_tab = st.tabs(["**Login**", "**Register**"])
    
    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            remember_me = st.checkbox("Remember Me", help="Keep me logged in for 7 days.")
            if st.form_submit_button("Login", use_container_width=True, type="primary"):
                with st.spinner("Logging in..."):
                    response = api.post("/users/token", data={"username": email, "password": password, "remember_me": str(remember_me).lower()})
                if response and response.status_code == 200:
                    token = response.json()["access_token"]
                    st.session_state['access_token'] = token
                    st.session_state['user_email'] = email
                    if remember_me:
                        localS.setItem("access_token", token, key="storage_access_token_set")
                        localS.setItem("user_email", email, key="storage_user_email_set")
                    st.toast("Login successful!", icon="🎉"); st.rerun()
                else:
                    st.error("Incorrect email or password.")
        
        if st.button("Forgot Password?", key="forgot_pass_btn"):
            st.session_state.show_forgot_password = True; st.rerun()

        if st.session_state.get('show_forgot_password'):
            with st.form("forgot_password_form", clear_on_submit=True):
                st.subheader("Reset Your Password")
                forgot_email = st.text_input("Enter your registered email", key="forgot_email")
                if st.form_submit_button("Send Reset Link"):
                    with st.spinner("Sending..."): api.post("/users/forgot-password", json={"email": forgot_email})
                    st.success("If an account with that email exists, a reset link has been sent."); time.sleep(2)
                    st.session_state.show_forgot_password = False; st.rerun()

    with register_tab:
        with st.form("register_form", clear_on_submit=True):
            full_name = st.text_input("Full Name")
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            if st.form_submit_button("Register", use_container_width=True):
                with st.spinner("Creating account..."):
                    response = api.post("/users/register", json={"full_name": full_name, "email": reg_email, "password": reg_password})
                if response and response.status_code == 201:
                    st.success("Account created! Please log in.")

def show_main_app_area():
    """Displays the main application dashboard for a logged-in user."""
    user_name = st.session_state.get('user_email', 'User').split('@')[0]
    st.title(f"Welcome, {user_name.capitalize()}!")
    st.markdown("This is your central hub for managing your health schedule.")
    st.markdown("---")

    with st.container(border=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Today at a Glance")
            with st.spinner("Loading summary..."):
                meds_resp = api.get("/medications/")
                apps_resp = api.get("/appointments/")
            
            active_meds_count = sum(1 for m in meds_resp.json() if m['is_active']) if meds_resp else 0
            today_apps_count = sum(1 for a in apps_resp.json() if datetime.fromisoformat(a['appointment_datetime']).date() == date.today()) if apps_resp else 0

            m_col1, m_col2 = st.columns(2)
            m_col1.metric("Active Medications", f"{active_meds_count} meds")
            m_col2.metric("Appointments Today", f"{today_apps_count} visits")

        with col2:
            st.subheader("Quick Actions")
            if st.button("➕ Add Medication", use_container_width=True): st.switch_page("pages/Medications.py")
            if st.button("🗓️ Schedule Appointment", use_container_width=True): st.switch_page("pages/Appointments.py")
            if st.button("🆘 Add Emergency Contact", use_container_width=True): st.switch_page("pages/Contacts.py")

    st.markdown("---")
    st.subheader("Navigate to a Section")
    nav_cols = st.columns(4)
    pages = {
        "Dashboard":    {"icon": "📈", "desc": "View your daily schedule and health tips.", "page": "pages/Dashboard.py"},
        "Medications":  {"icon": "💊", "desc": "Add, edit, or view your medication list.", "page": "pages/Medications.py"},
        "Appointments": {"icon": "🗓️", "desc": "Keep track of all your doctor visits.", "page": "pages/Appointments.py"},
        "Settings":     {"icon": "⚙️", "desc": "Update your profile and preferences.", "page": "pages/Settings.py"}
    }
    for i, (page_name, details) in enumerate(pages.items()):
        with nav_cols[i]:
            with st.container(border=True):
                st.markdown(f"### {details['icon']} {page_name}")
                st.caption(details['desc'])
                if st.button(f"Go to {page_name}", use_container_width=True, key=f"nav_{page_name}"):
                    st.switch_page(details['page'])

# --- 10. MAIN APPLICATION CONTROLLER ---
def main():
    """Controls the application flow."""
    if 'access_token' not in st.session_state:
        try:
            token = localS.getItem("access_token", key="storage_access_token_get")
            email = localS.getItem("user_email", key="storage_user_email_get")
            if token and email:
                st.session_state['access_token'] = token
                st.session_state['user_email'] = email
                st.rerun()
        except TypeError:
            pass

    if "access_token" not in st.session_state:
        show_login_register_page()
    else:
        build_sidebar()
        create_header()
        create_sos_bar()
        show_main_app_area()

if __name__ == "__main__":
    main()
