# /frontend/pages/Appointments.py

import os
from datetime import datetime

import requests
import streamlit as st
from streamlit_calendar import calendar

# --- 1. PAGE CONFIGURATION ---
# YAHI FIX HAI: `icon` ko `page_icon` se badal diya gaya hai.
st.set_page_config(page_title="My Appointments", layout="wide", page_icon="🗓️")

# --- 2. Custom UI Components ---
from ui_components import apply_styles, build_sidebar

# --- 3. APPLY STYLES & SIDEBAR ---
apply_styles()
build_sidebar()

# --- 4. API & SESSION STATE SETUP ---
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

class ApiClient:
    def __init__(self, base_url: str): self.base_url = base_url
    def _get_headers(self) -> dict:
        token = st.session_state.get("access_token")
        if not token:
            st.warning("Your session has expired. Please login again.")
            st.switch_page("streamlit_app.py"); st.stop()
        return {"Authorization": f"Bearer {token}"}
    def _make_request(self, method: str, endpoint: str, **kwargs):
        try:
            response = requests.request(f"{self.base_url}{endpoint}", headers=self._get_headers(), timeout=15, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            st.error(f"API Error: {e.response.json().get('detail', 'Unknown error')}")
        except requests.exceptions.ConnectionError: st.error("Connection Error.")
        return None
    def get(self, endpoint: str): return self._make_request("GET", endpoint)
    def post(self, endpoint: str, json_data: dict): return self._make_request("POST", endpoint, json=json_data)
    def put(self, endpoint: str, json_data: dict): return self._make_request("PUT", endpoint, json=json_data)
    def delete(self, endpoint: str): return self._make_request("DELETE", endpoint)

api = ApiClient(API_BASE_URL)

if 'access_token' not in st.session_state:
    st.warning("Please login first to access this page.")
    st.switch_page("streamlit_app.py"); st.stop()

def fetch_appointments():
    response = api.get("/appointments/")
    if response and response.status_code == 200:
        st.session_state.appointments = sorted(response.json(), key=lambda x: x['appointment_datetime'], reverse=True)
    else: st.session_state.appointments = []

if 'appointments' not in st.session_state:
    with st.spinner("Loading appointments..."): fetch_appointments()

st.header("🗓️ My Appointments")
st.write("View your schedule on the calendar. Click an appointment to edit or delete it.")
st.markdown("---")

calendar_events = []
for app in st.session_state.get('appointments', []):
    dt_obj = datetime.fromisoformat(app['appointment_datetime'])
    calendar_events.append({"title": f"Dr. {app['doctor_name']}", "start": dt_obj.isoformat(), "end": dt_obj.isoformat(), "extendedProps": {"id": app['id']}})
calendar_options = {"headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,timeGridWeek,timeGridDay,listMonth"}, "initialView": "dayGridMonth"}
clicked_event = calendar(events=calendar_events, options=calendar_options, key="appointment_calendar")

if clicked_event and clicked_event.get("event"):
    clicked_app_id = int(clicked_event["event"]["extendedProps"]["id"])
    if st.session_state.get('edit_app_id') != clicked_app_id:
        st.session_state.edit_mode_app = True; st.session_state.edit_app_id = clicked_app_id; st.rerun()

is_edit_mode = st.session_state.get('edit_mode_app', False)
expander_title = "✏️ Edit Selected Appointment" if is_edit_mode else "➕ Add New Appointment"
with st.expander(expander_title, expanded=is_edit_mode or not st.session_state.get('appointments')):
    with st.container(border=True):
        edit_app_id = st.session_state.get('edit_app_id')
        default_values = {}
        if is_edit_mode and edit_app_id:
            app_to_edit = next((a for a in st.session_state.appointments if a['id'] == edit_app_id), None)
            if app_to_edit:
                dt_obj = datetime.fromisoformat(app_to_edit.get('appointment_datetime'))
                default_values = {"doctor_name": app_to_edit.get('doctor_name', ''), "purpose": app_to_edit.get('purpose', ''), "location": app_to_edit.get('location', ''), "date": dt_obj.date(), "time": dt_obj.time()}
        with st.form("app_form"):
            doctor_name = st.text_input("Doctor's Name / Hospital*", value=default_values.get('doctor_name', ''))
            purpose = st.text_input("Purpose of Visit", value=default_values.get('purpose', ''))
            location = st.text_input("Location / Address", value=default_values.get('location', ''))
            col1, col2 = st.columns(2)
            with col1: app_date = st.date_input("Date*", value=default_values.get('date', datetime.now().date()))
            with col2: app_time = st.time_input("Time*", value=default_values.get('time', datetime.now().time()))
            b_col1, b_col2, b_col3, b_col4 = st.columns([3, 1, 1, 2])
            with b_col1: save_button = st.form_submit_button("💾 Save Appointment", type="primary", use_container_width=True)
            if is_edit_mode:
                with b_col2: delete_button = st.form_submit_button("🗑️ Delete", use_container_width=True)
                with b_col3: cancel_button = st.form_submit_button("✖️ Cancel", use_container_width=True)
            else: delete_button = cancel_button = False
            if save_button:
                if not doctor_name: st.warning("Doctor's Name is required.")
                else:
                    app_data = {"doctor_name": doctor_name.strip(), "purpose": purpose.strip(), "location": location.strip(), "appointment_datetime": datetime.combine(app_date, app_time).isoformat()}
                    if is_edit_mode: response = api.put(f"/appointments/{st.session_state.edit_app_id}", json_data=app_data)
                    else: response = api.post("/appointments/", json_data=app_data)
                    if response:
                        st.toast("Saved successfully!", icon="✅"); st.session_state.edit_mode_app = False; st.session_state.pop('edit_app_id', None); fetch_appointments(); st.rerun()
            if delete_button:
                if api.delete(f"/appointments/{st.session_state.edit_app_id}"):
                    st.toast("Appointment deleted.", icon="🗑️"); st.session_state.edit_mode_app = False; st.session_state.pop('edit_app_id', None); fetch_appointments(); st.rerun()
            if cancel_button: st.session_state.edit_mode_app = False; st.session_state.pop('edit_app_id', None); st.rerun()
