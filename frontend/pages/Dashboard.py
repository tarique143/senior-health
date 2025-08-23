# /frontend/pages/Dashboard.py (Final Version)

import streamlit as st
import requests
from datetime import datetime

# Hamari nayi UI file se functions import karein
from ui_components import apply_styles, build_sidebar

# Page ki shuruaat mein styles aur double-sidebar fix apply karein
apply_styles()

# --- CONFIGURATION & API CLIENT ---
API_BASE_URL = st.secrets.get("API_BASE_URL", "http://127.0.0.1:8000")

class ApiClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = st.session_state.get("access_token", None)
    def _get_headers(self):
        if self.token: return {"Authorization": f"Bearer {self.token}"}
        return {}
    def _make_request(self, method, endpoint, **kwargs):
        try:
            return requests.request(method, f"{self.base_url}{endpoint}", headers=self._get_headers(), **kwargs)
        except requests.exceptions.ConnectionError:
            st.error("Connection Error: Could not connect to the backend server.")
            return None
    def get(self, endpoint, params=None):
        return self._make_request("GET", endpoint, params=params)

api = ApiClient(API_BASE_URL)

# --- SECURITY CHECK ---
if 'access_token' not in st.session_state:
    st.warning("Please login first to access this page.")
    st.switch_page("streamlit_app.py")
    st.stop()

# --- PAGE SETUP ---
st.set_page_config(page_title="Dashboard - Health Companion", layout="wide")
build_sidebar() # Hamara custom sidebar banayein

# --- STYLING for this page ---
st.markdown("""
    <style>
        .call-link {
            display: block; padding: 12px; background-color: #ffe3e3;
            border-radius: 8px; text-align: center; text-decoration: none;
            color: #c92a2a; font-weight: bold; margin-bottom: 10px; border: 1px solid #ffc9c9;
        }
        .call-link:hover { background-color: #ffc9c9; color: #a71c1c; }
        [data-baseweb="theme-dark"] .call-link {
            background-color: #5c1a1a; border: 1px solid #a71c1c; color: #ffc9c9;
        }
        [data-baseweb="theme-dark"] .call-link:hover {
            background-color: #a71c1c; color: white;
        }
    </style>
""", unsafe_allow_html=True)

# --- DASHBOARD PAGE CONTENT ---
st.header("Today's Dashboard")
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("🗓️ Today's Appointments")
        response = api.get("/appointments/")
        if response and response.status_code == 200:
            appointments = response.json()
            today = datetime.now().date()
            today_apps = [app for app in appointments if datetime.fromisoformat(app['appointment_datetime']).date() == today]
            if today_apps:
                for app in sorted(today_apps, key=lambda x: x['appointment_datetime']):
                    st.info(f"**{app['doctor_name']}** at {datetime.fromisoformat(app['appointment_datetime']).strftime('%I:%M %p')}")
            else:
                st.write("You have no appointments scheduled for today.")
        else:
            st.warning("Could not fetch appointments.")

    with st.container(border=True):
        st.subheader("💊 Today's Medications")
        response = api.get("/medications/")
        if response and response.status_code == 200:
            meds = [m for m in response.json() if m['is_active']]
            if meds:
                for med in sorted(meds, key=lambda x: datetime.strptime(x['timing'], '%H:%M:%S').time()):
                    st.success(f"**{med['name']}** ({med['dosage']}) at {datetime.strptime(med['timing'], '%H:%M:%S').strftime('%I:%M %p')}")
            else:
                st.write("You have no active medications scheduled.")
        else:
            st.warning("Could not fetch medications.")

with col2:
    with st.container(border=True):
        st.subheader("📞 Emergency Contacts")
        response = api.get("/contacts/")
        if response and response.status_code == 200:
            contacts = response.json()
            if contacts:
                for contact in contacts:
                    phone_number = contact['phone_number']
                    st.markdown(f'<a href="tel:{phone_number}" class="call-link">Call {contact["name"]}<br><small>{phone_number}</small></a>', unsafe_allow_html=True)
            else:
                st.write("You have not added any emergency contacts yet.")
        else:
            st.warning("Could not fetch contacts.")
    
    with st.container(border=True):
        st.subheader("💡 Today's Health Tip")
        response = api.get("/tips/random")
        if response and response.status_code == 200:
            tip = response.json()
            st.info(f"**{tip['category']}:** {tip['content']}")
        else:
            st.warning("Could not fetch a health tip. Add tips via the backend API docs.")
