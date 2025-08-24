# /frontend/pages/Dashboard.py

import os
from datetime import date, datetime

import requests
import streamlit as st

# --- 1. PAGE CONFIGURATION ---
# YAHI FIX HAI: `icon` ko `page_icon` se badal diya gaya hai.
st.set_page_config(page_title="Dashboard", layout="wide", page_icon="📈")

# --- 2. Custom UI Components ---
# Correctly placed after page config.
from ui_components import apply_styles, build_sidebar

# --- 3. APPLY STYLES & SIDEBAR ---
apply_styles()
build_sidebar()

# --- 4. API & SESSION STATE SETUP ---
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

class ApiClient:
    """A simple client to interact with the backend API."""
    def __init__(self, base_url: str):
        self.base_url = base_url
    def _get_headers(self) -> dict:
        token = st.session_state.get("access_token")
        if not token:
            st.warning("Your session has expired. Please login again.")
            st.switch_page("streamlit_app.py"); st.stop()
        return {"Authorization": f"Bearer {token}"}
    def _make_request(self, method: str, endpoint: str, **kwargs):
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method, url, headers=self._get_headers(), timeout=15, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException: return None
    def get(self, endpoint: str): return self._make_request("GET", endpoint)

api = ApiClient(API_BASE_URL)

# --- Security Check ---
if 'access_token' not in st.session_state:
    st.warning("Please login first to access this page.")
    st.switch_page("streamlit_app.py"); st.stop()

# --- STYLING for this page ---
st.markdown("""<style>.call-link {display: block; padding: 10px 15px; background-color: #e0f7fa; border-left: 5px solid #00796b; border-radius: 5px; margin-bottom: 10px; text-decoration: none; color: #004d40; transition: background-color 0.2s;} .call-link:hover { background-color: #b2dfdb; } .strikethrough { text-decoration: line-through; color: #888; }</style>""", unsafe_allow_html=True)

# --- State Management for Today's Checklist ---
today_str = date.today().isoformat()
if f"taken_meds_{today_str}" not in st.session_state:
    st.session_state[f"taken_meds_{today_str}"] = []

def handle_take_med(med_id: int):
    if med_id not in st.session_state[f"taken_meds_{today_str}"]:
        st.session_state[f"taken_meds_{today_str}"].append(med_id)

# --- DATA FETCHING (with Caching) ---
@st.cache_data(ttl=300)
def get_dashboard_data():
    meds_resp, apps_resp, tips_resp, contacts_resp = api.get("/medications/"), api.get("/appointments/"), api.get("/tips/random"), api.get("/contacts/")
    meds = meds_resp.json() if meds_resp and meds_resp.status_code == 200 else []
    apps = apps_resp.json() if apps_resp and apps_resp.status_code == 200 else []
    tip = tips_resp.json() if tips_resp and tips_resp.status_code == 200 else None
    contacts = contacts_resp.json() if contacts_resp and contacts_resp.status_code == 200 else []
    return meds, apps, tip, contacts

with st.spinner("Loading your dashboard..."):
    all_meds, all_apps, health_tip, contacts = get_dashboard_data()

# --- Process Data for Today ---
active_meds_today = [m for m in all_meds if m['is_active']]
today = datetime.now().date()
today_apps = [app for app in all_apps if datetime.fromisoformat(app['appointment_datetime']).date() == today]

# --- Main Page Content ---
st.header("📈 Your Daily Dashboard")
user_name = st.session_state.get('user_email', '').split('@')[0].capitalize()
st.markdown(f"Hello **{user_name}**! Here’s your summary for today, **{today.strftime('%B %d, %Y')}**.")
st.markdown("---")

# --- Medication Progress Bar ---
taken_count = len(st.session_state[f"taken_meds_{today_str}"])
total_meds = len(active_meds_today)
if total_meds > 0:
    st.progress(taken_count / total_meds, text=f"Medications Completed: {taken_count} of {total_meds}")
else:
    st.success("You have no active medications scheduled for today. Enjoy your day!")

st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("💊 Today's Medication Checklist")
        if not active_meds_today: st.write("No active medications found.")
        else:
            sorted_meds = sorted(active_meds_today, key=lambda x: datetime.strptime(x['timing'], '%H:%M:%S').time())
            for med in sorted_meds:
                med_id = med['id']
                is_taken = med_id in st.session_state[f"taken_meds_{today_str}"]
                c1, c2 = st.columns([4, 2])
                with c1:
                    med_time = datetime.strptime(med['timing'], '%H:%M:%S').strftime('%I:%M %p')
                    label = f"**{med['name']}** ({med['dosage']}) at `{med_time}`"
                    if is_taken: st.markdown(f"<span class='strikethrough'>{label}</span>", unsafe_allow_html=True)
                    else: st.markdown(label)
                with c2:
                    st.button("Mark as Taken", key=f"take_med_{med_id}", on_click=handle_take_med, args=(med_id,), use_container_width=True, disabled=is_taken)

    with st.container(border=True):
        st.subheader("🗓️ Today's Appointments")
        if not today_apps: st.write("You have no appointments scheduled for today.")
        else:
            for app in sorted(today_apps, key=lambda x: x['appointment_datetime']):
                app_time = datetime.fromisoformat(app['appointment_datetime']).strftime('%I:%M %p')
                st.info(f"**Dr. {app['doctor_name']}** at **{app_time}** for '{app.get('purpose', 'a check-up')}'")

with col2:
    with st.container(border=True):
        st.subheader("🆘 Emergency Contacts")
        if contacts:
            for contact in contacts[:3]: st.markdown(f'<a href="tel:{contact["phone_number"]}" class="call-link" target="_blank">Call {contact["name"]}<br><small>{contact["phone_number"]}</small></a>', unsafe_allow_html=True)
        else:
            st.write("No emergency contacts added yet.")
            if st.button("Add a Contact"): st.switch_page("pages/Contacts.py")

    with st.container(border=True):
        st.subheader("💡 Today's Health Tip")
        if health_tip: st.info(f"**{health_tip['category']}:** {health_tip['content']}")
        else: st.warning("Could not fetch a health tip right now.")
