import streamlit as st
import requests
from datetime import datetime, date
import os

# 1. Sabse pehla Streamlit command hamesha st.set_page_config hona chahiye
st.set_page_config(page_title="Dashboard - Health Companion", layout="wide")

# 2. Uske baad baaki imports aur setup
from ui_components import apply_styles, build_sidebar
apply_styles()

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# --- API CLIENT CLASS ---
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
            st.error("Connection Error."); return None
    def get(self, endpoint, params=None):
        return self._make_request("GET", endpoint, params=params)

api = ApiClient(API_BASE_URL)

# --- SECURITY CHECK ---
if 'access_token' not in st.session_state:
    st.warning("Please login first to access this page.")
    st.switch_page("streamlit_app.py")
    st.stop()

# --- SIDEBAR ---
build_sidebar()

# --- STYLING for this page ---
st.markdown("""
    <style>
        .call-link { /* ... (styling code waisa hi rahega) ... */ }
        .strikethrough { text-decoration: line-through; color: #888; }
    </style>
""", unsafe_allow_html=True)

# --- STATE MANAGEMENT FOR CHECKLIST ---
today_str = date.today().isoformat()
if f"taken_meds_{today_str}" not in st.session_state:
    st.session_state[f"taken_meds_{today_str}"] = []

def handle_take_med(med_id):
    st.session_state[f"taken_meds_{today_str}"].append(med_id)

# --- DATA FETCHING ---
@st.cache_data(ttl=300)
def get_dashboard_data():
    meds = api.get("/medications/")
    apps = api.get("/appointments/")
    tips = api.get("/tips/random")
    contacts = api.get("/contacts/")
    return meds, apps, tips, contacts

meds_response, apps_response, tips_response, contacts_response = get_dashboard_data()

# --- PAGE CONTENT ---
active_meds_today = []
if meds_response and meds_response.status_code == 200:
    active_meds_today = [m for m in meds_response.json() if m['is_active']]
today_apps = []
if apps_response and apps_response.status_code == 200:
    today = datetime.now().date()
    today_apps = [app for app in apps_response.json() if datetime.fromisoformat(app['appointment_datetime']).date() == today]

st.header(f"Your Daily Dashboard")
st.markdown(f"Hello **{st.session_state.get('user_email', '').split('@')[0].capitalize()}**! You have **{len(active_meds_today)}** medications and **{len(today_apps)}** appointments scheduled for today.")
st.markdown("---")

# Medication Progress Bar
taken_count = len(st.session_state[f"taken_meds_{today_str}"])
total_meds = len(active_meds_today)
if total_meds > 0:
    progress = taken_count / total_meds
    st.progress(progress, text=f"Medications Completed: {taken_count} of {total_meds}")
else:
    st.success("No active medications scheduled for today. Relax!")

col1, col2 = st.columns(2)

with col1:
    # --- INTERACTIVE MEDICATION CHECKLIST ---
    with st.container(border=True):
        st.subheader("💊 Today's Medication Checklist")
        if active_meds_today:
            sorted_meds = sorted(active_meds_today, key=lambda x: datetime.strptime(x['timing'], '%H:%M:%S').time())
            for med in sorted_meds:
                med_id = med['id']
                is_taken = med_id in st.session_state[f"taken_meds_{today_str}"]
                
                c1, c2 = st.columns([4, 1.5])
                with c1:
                    med_time = datetime.strptime(med['timing'], '%H:%M:%S').strftime('%I:%M %p')
                    if is_taken:
                        st.markdown(f"<span class='strikethrough'>**{med['name']}** ({med['dosage']}) at {med_time}</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"**{med['name']}** ({med['dosage']}) at `{med_time}`")
                with c2:
                    if is_taken:
                        st.success("Taken ✔", icon="✅")
                    else:
                        st.button("Mark as Taken", key=f"take_med_{med_id}", on_click=handle_take_med, args=(med_id,), use_container_width=True)
        else:
            st.write("No active medications found.")

    # --- TODAY'S APPOINTMENTS ---
    with st.container(border=True):
        st.subheader("🗓️ Today's Appointments")
        if today_apps:
            for app in sorted(today_apps, key=lambda x: x['appointment_datetime']):
                st.info(f"**Dr. {app['doctor_name']}** at **{datetime.fromisoformat(app['appointment_datetime']).strftime('%I:%M %p')}** for '{app.get('purpose', 'a check-up')}'")
        else:
            st.write("You have no appointments scheduled for today.")

with col2:
    # --- EMERGENCY CONTACTS ---
    with st.container(border=True):
        st.subheader("📞 Emergency Contacts")
        if contacts_response and contacts_response.status_code == 200 and contacts_response.json():
            for contact in contacts_response.json()[:3]: # Sirf pehle 3 dikhayein
                st.markdown(f'<a href="tel:{contact["phone_number"]}" class="call-link">Call {contact["name"]}<br><small>{contact["phone_number"]}</small></a>', unsafe_allow_html=True)
        else:
            st.write("No emergency contacts added yet.")

    # --- HEALTH TIP ---
    with st.container(border=True):
        st.subheader("💡 Today's Health Tip")
        if tips_response and tips_response.status_code == 200:
            tip = tips_response.json()
            st.info(f"**{tip['category']}:** {tip['content']}")
        else:
            st.warning("Could not fetch a health tip.")
