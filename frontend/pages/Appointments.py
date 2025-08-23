# frontend/pages/Appointments.py (Final Version with Calendar View)

import streamlit as st
import requests
import os
from datetime import datetime

# Calendar library import karein
from streamlit_calendar import calendar

# --- CONFIGURATION & API CLIENT ---
st.set_page_config(page_title="My Appointments", layout="wide")
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

class ApiClient:
    def __init__(self, base_url): self.base_url = base_url
    def _get_headers(self):
        token = st.session_state.get("access_token")
        if not token: st.warning("Please login first."); st.switch_page("streamlit_app.py"); st.stop()
        return {"Authorization": f"Bearer {token}"}
    def _make_request(self, method, endpoint, **kwargs):
        try: return requests.request(method, f"{self.base_url}{endpoint}", headers=self._get_headers(), timeout=10, **kwargs)
        except requests.exceptions.RequestException: st.error("Connection Error: Could not connect to the backend server."); return None
    def get(self, endpoint): return self._make_request("GET", endpoint)
    def post(self, endpoint, json=None): return self._make_request("POST", endpoint, json=json)
    def put(self, endpoint, json=None): return self._make_request("PUT", endpoint, json=json)
    def delete(self, endpoint): return self._make_request("DELETE", endpoint)

api = ApiClient(API_BASE_URL)

# --- SECURITY CHECK ---
if 'access_token' not in st.session_state:
    st.warning("Please login first to access this page.")
    st.switch_page("streamlit_app.py")
    st.stop()

# --- HELPER FUNCTIONS ---
def fetch_appointments():
    response = api.get("/appointments/")
    if response and response.status_code == 200:
        st.session_state.appointments = sorted(response.json(), key=lambda x: x['appointment_datetime'], reverse=True)
    else:
        st.session_state.appointments = []
        st.error("Could not fetch appointments.")

# --- INITIAL DATA FETCH ---
if 'appointments' not in st.session_state:
    fetch_appointments()

# --- PAGE CONTENT ---
st.header("🗓️ My Appointments")
st.write("View your schedule on the calendar. Click on an appointment to edit it.")
st.markdown("---")

# --- CALENDAR VIEW ---

# API se aaye data ko calendar ke format mein badlein
calendar_events = []
for app in st.session_state.get('appointments', []):
    calendar_events.append({
        "title": f"Dr. {app['doctor_name']}",
        "start": app['appointment_datetime'],
        "end": app['appointment_datetime'],
        "extendedProps": {"id": app['id']}
    })

# Calendar ke options set karein
calendar_options = {
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,timeGridDay,listMonth",
    },
    "initialView": "dayGridMonth",
    "slotMinTime": "06:00:00",
    "slotMaxTime": "22:00:00",
    "editable": False,
    "navLinks": True,
}

# Calendar ko display karein
clicked_event = calendar(
    events=calendar_events,
    options=calendar_options,
    custom_css="""
        .fc-event-past { opacity: 0.7; }
        .fc-event-time { font-style: italic; }
        .fc-event-title { font-weight: 700; }
        .fc-toolbar-title { font-size: 1.5rem; }
    """,
    key="appointment_calendar"
)

# Agar user ne kisi event par click kiya hai, to edit mode on karein
if clicked_event and clicked_event.get("event"):
    clicked_app_id = int(clicked_event["event"]["extendedProps"]["id"])
    if st.session_state.get('edit_app_id') != clicked_app_id:
        st.session_state.edit_mode_app = True
        st.session_state.edit_app_id = clicked_app_id
        st.rerun()

# --- FORM TO ADD/EDIT APPOINTMENT ---
st.markdown("---")
expander_title = "➕ Add New Appointment"
if st.session_state.get('edit_mode_app'):
    expander_title = "✏️ Edit Selected Appointment"

with st.expander(expander_title, expanded=st.session_state.get('edit_mode_app', False)):
    edit_app_id = st.session_state.get('edit_app_id')
    default_values = {}
    if edit_app_id and 'appointments' in st.session_state:
        app_to_edit = next((a for a in st.session_state.appointments if a['id'] == edit_app_id), None)
        if app_to_edit:
            dt_obj = datetime.fromisoformat(app_to_edit.get('appointment_datetime'))
            default_values = {
                "doctor_name": app_to_edit.get('doctor_name', ''),
                "purpose": app_to_edit.get('purpose', ''),
                "location": app_to_edit.get('location', ''),
                "date": dt_obj.date(),
                "time": dt_obj.time()
            }

    with st.form("app_form", clear_on_submit=False):
        # --- COMPLETE FORM FIELDS ---
        doctor_name = st.text_input("Doctor's Name / Hospital", value=default_values.get('doctor_name', ''))
        purpose = st.text_input("Purpose of Visit", value=default_values.get('purpose', ''))
        location = st.text_input("Location / Address", value=default_values.get('location', ''))
        
        col1, col2 = st.columns(2)
        with col1:
            app_date = st.date_input("Date", value=default_values.get('date', datetime.now().date()))
        with col2:
            app_time = st.time_input("Time", value=default_values.get('time', datetime.now().time()))
        # --- END OF FORM FIELDS ---
        
        # Form buttons
        b_col1, b_col2, b_col3 = st.columns([2, 1, 1])
        with b_col1:
            if st.form_submit_button("💾 Save Appointment", type="primary", use_container_width=True):
                if not doctor_name:
                    st.warning("Doctor's Name is required.")
                else:
                    appointment_datetime = datetime.combine(app_date, app_time).isoformat()
                    app_data = {"doctor_name": doctor_name, "purpose": purpose, "location": location, "appointment_datetime": appointment_datetime}
                    
                    if st.session_state.get('edit_mode_app'):
                        response = api.put(f"/appointments/{st.session_state.edit_app_id}", json=app_data)
                        if response and response.status_code == 200: st.toast("Appointment updated!", icon="✅")
                        else: st.error("Failed to update appointment.")
                    else:
                        response = api.post("/appointments/", json=app_data)
                        if response and response.status_code == 201: st.toast("Appointment added!", icon="🎉")
                        else: st.error("Failed to add appointment.")
                    
                    st.session_state.edit_mode_app = False
                    st.session_state.pop('edit_app_id', None)
                    fetch_appointments()
                    st.rerun()

        with b_col2:
            if st.session_state.get('edit_mode_app'):
                if st.form_submit_button("🗑️ Delete", use_container_width=True):
                    response = api.delete(f"/appointments/{st.session_state.edit_app_id}")
                    if response and response.status_code == 204: st.toast("Appointment deleted.", icon="🗑️")
                    else: st.error("Failed to delete appointment.")
                    
                    st.session_state.edit_mode_app = False
                    st.session_state.pop('edit_app_id', None)
                    fetch_appointments()
                    st.rerun()
        with b_col3:
            if st.session_state.get('edit_mode_app'):
                if st.form_submit_button("✖️ Cancel", use_container_width=True):
                    st.session_state.edit_mode_app = False
                    st.session_state.pop('edit_app_id', None)
                    st.rerun()

# Display past appointments in an expander
st.markdown("---")
with st.expander("View Past Appointments"):
    now = datetime.now()
    past_apps = [app for app in st.session_state.appointments if datetime.fromisoformat(app['appointment_datetime']) < now]
    if past_apps:
        for app in past_apps: # Already sorted by most recent first
            dt_obj = datetime.fromisoformat(app['appointment_datetime'])
            st.info(f"**{dt_obj.strftime('%d-%b-%Y')}**: Dr. {app['doctor_name']} for {app.get('purpose', 'a check-up')}.")
    else:
        st.write("No past appointments found.")
