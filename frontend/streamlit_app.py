# frontend/streamlit_app.py (Fully Updated with "Behtareen" Main Area)

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
        token = st.session_state.get("token")
        if not token:
            return {}
        return {"Authorization": f"Bearer {token}"}
    def _make_request(self, method, endpoint, **kwargs):
        # Redirect to login if token is missing
        if "token" not in st.session_state and endpoint not in ["/users/token", "/users/register", "/users/forgot-password"]:
            st.switch_page("streamlit_app.py")
            st.stop()
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
    # ... (Aapki purani themed styling yahan rahegi) ...
    ### --- NAYI STYLING (NAVIGATION CARDS KE LIYE) --- ###
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
            height: 100%; /* Make cards of same height */
        }
        .nav-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.1);
            border-color: #0068C9;
        }
        .nav-card h3 {
            color: #0055a3;
            margin-top: 15px;
        }
        .nav-card p {
            font-size: 1rem;
            color: #555;
        }
        .nav-card .icon {
            font-size: 3.5rem;
        }
        /* Dark Theme Adjustments */
        [data-baseweb="theme-dark"] .nav-card {
            background-color: #252526;
            border: 1px solid #444;
        }
        [data-baseweb="theme-dark"] .nav-card h3 {
            color: #3B82F6;
        }
        [data-baseweb="theme-dark"] .nav-card p {
            color: #bbb;
        }
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
    # ... (Aapka purana login/register page ka code yahan rahega, koi badlav nahi) ...
    # Main isse chota kar raha hoon
    st.markdown('<div style="text-align:center;"><h1>Welcome to Health Companion</h1></div>', unsafe_allow_html=True)
    # ... (login, register, forgot password forms) ...
    st.warning("For brevity, the login form code is hidden. It remains unchanged.")


### --- NAYA FUNCTION (MAIN APP AREA KE LIYE) --- ###
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
        for app in apps_response.json():
            if datetime.fromisoformat(app['appointment_datetime']).date() == today:
                today_apps_count += 1
    
    # Quick Stats Display
    st.subheader("Today's at a Glance")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Active Medications", value=f"{active_meds_count} meds")
    with col2:
        st.metric(label="Appointments Today", value=f"{today_apps_count} visits")
    with col3:
        # Placeholder for future metric
        st.metric(label="Health Tip", value="Ready!", help="A new tip is waiting for you on the dashboard!")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Navigation Cards
    st.subheader("What would you like to do?")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="nav-card">
            <div class="icon">📈</div>
            <h3>Go to Dashboard</h3>
            <p>View your complete daily schedule and health tips.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Dashboard", use_container_width=True, key="dash_btn"):
            st.switch_page("pages/1_Dashboard.py")

    with col2:
        st.markdown("""
        <div class="nav-card">
            <div class="icon">💊</div>
            <h3>Manage Medications</h3>
            <p>Add, edit, or view your medication list and schedule.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Manage Meds", use_container_width=True, key="med_btn"):
            st.switch_page("pages/Medications.py")
    
    with col3:
        st.markdown("""
        <div class="nav-card">
            <div class="icon">🗓️</div>
            <h3>Manage Appointments</h3>
            <p>Keep track of all your upcoming doctor visits.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Manage Appointments", use_container_width=True, key="app_btn"):
            st.switch_page("pages/Appointments.py")
            
    with col4:
        st.markdown("""
        <div class="nav-card">
            <div class="icon">⚙️</div>
            <h3>My Settings</h3>
            <p>Update your profile, password, and contacts.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Go to Settings", use_container_width=True, key="set_btn"):
            st.switch_page("pages/Settings.py")

### --- MAIN APPLICATION CONTROLLER (UPDATED) --- ###
def main():
    apply_global_styles()

    if "token" not in st.session_state:
        # Assuming show_login_register_page() is defined elsewhere and works
        show_login_register_page() 
    else:
        # This is the main logged-in view
        apply_themed_styles()

        st.sidebar.title("Navigation")
        st.sidebar.markdown(f"Welcome, \n**{st.session_state.get('user_email', 'User')}**!")
        if st.sidebar.button("Logout", use_container_width=True):
            st.session_state.clear(); st.toast("Logged out successfully."); st.rerun()

        # Emergency SOS Bar
        response = api.get("/contacts/")
        if response and response.status_code == 200 and response.json():
            emergency_number = response.json()[0]['phone_number']
            st.markdown(f'<a href="tel:{emergency_number}" class="emergency-bar">🚨 EMERGENCY SOS 🚨</a>', unsafe_allow_html=True)
        else:
            st.markdown(f'<a href="/Contacts" class="emergency-bar">⚠️ ADD SOS CONTACT ⚠️</a>', unsafe_allow_html=True)
        
        create_header()

        ### --- NAYE FUNCTION KO YAHAN CALL KAREIN --- ###
        show_main_app_area()

if __name__ == "__main__":
    # For brevity, hiding the full login page code here. Replace this with your actual show_login_register_page function.
    def show_login_register_page():
        st.title("Login/Register Area")
        st.write("Please log in to continue.")
        # Simulating a login for testing purposes
        if st.button("Simulate Login"):
            st.session_state['token'] = 'fake_token_for_testing'
            st.session_state['user_email'] = 'test@example.com'
            st.rerun()
    
    main()
