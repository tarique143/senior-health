# /frontend/pages/Appointments.py

import os
from datetime import datetime

import requests
import streamlit as st
# The streamlit-calendar component for displaying an interactive calendar.
from streamlit_calendar import calendar

# --- 1. PAGE CONFIGURATION ---
# This must be the first Streamlit command in the script.
st.set_page_config(page_title="My Appointments", layout="wide", icon="🗓️")

# --- 2. Custom UI Components ---
# Import custom components after setting the page config.
from ui_components import apply_styles, build_sidebar

# --- 3. APPLY STYLES & SIDEBAR ---
apply_styles()
build_sidebar()

# --- 4. API & SESSION STATE SETUP ---

# Configuration for the backend API URL.
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

class ApiClient:
    """A simple client to interact with the backend API."""
    def __init__(self, base_url: str):
        self.base_url = base_url

    def _get_headers(self) -> dict:
        """Constructs authorization headers with the user's access token."""
        token = st.session_state.get("access_token")
        if not token:
            st.warning("Your session has expired. Please login again.")
            st.switch_page("streamlit_app.py")
            st.stop()
        return {"Authorization": f"Bearer {token}"}

    def _make_request(self, method: str, endpoint: str, **kwargs):
        """Makes an HTTP request to the API and handles common errors."""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method, url, headers=self._get_headers(), timeout=15, **kwargs)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            return response
        except requests.exceptions.HTTPError as e:
            st.error(f"API Error: {e.response.json().get('detail', 'Unknown error')}")
        except requests.exceptions.ConnectionError:
            st.error("Connection Error: Could not connect to the server.")
        except requests.exceptions.RequestException as e:
            st.error(f"An unexpected error occurred: {e}")
        return None

    def get(self, endpoint: str): return self._make_request("GET", endpoint)
    def post(self, endpoint: str, json_data: dict): return self._make_request("POST", endpoint, json=json_data)
    def put(self, endpoint: str, json_data: dict): return self._make_request("PUT", endpoint, json=json_data)
    def delete(self, endpoint: str): return self._make_request("DELETE", endpoint)

api = ApiClient(API_BASE_URL)

# --- Security Check: Ensure the user is logged in ---
if 'access_token' not in st.session_state:
    st.warning("Please login first to access this page.")
    st.switch_page("streamlit_app.py")
    st.stop()

# --- Helper Function for Fetching Data ---
def fetch_appointments():
    """Fetches appointments from the API and stores them in the session state."""
    response = api.get("/appointments/")
    if response and response.status_code == 200:
        # Sort by date, with the newest appointments first.
        st.session_state.appointments = sorted(
            response.json(), key=lambda x: x['appointment_datetime'], reverse=True
        )
    else:
        st.session_state.appointments = []
        # Error is already shown by ApiClient, so no need for another st.error here.

# --- Initial Data Fetch ---
if 'appointments' not in st.session_state:
    with st.spinner("Loading your appointments..."):
        fetch_appointments()


# --- Main Page Content ---
st.header("🗓️ My Appointments")
st.write("View your schedule on the calendar. Click an appointment to edit or delete it.")
st.markdown("---")

# --- 1. CALENDAR VIEW ---
calendar_events = []
for app in st.session_state.get('appointments', []):
    # Ensure start and end times are in ISO format for the calendar component.
    dt_obj = datetime.fromisoformat(app['appointment_datetime'])
    calendar_events.append({
        "title": f"Dr. {app['doctor_name']}",
        "start": dt_obj.isoformat(),
        "end": dt_obj.isoformat(),
        "extendedProps": {"id": app['id']}
    })

calendar_options = {
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,timeGridDay,listMonth"
    },
    "initialView": "dayGridMonth",
    "slotMinTime": "06:00:00",
    "slotMaxTime": "22:00:00",
    "editable": False,
    "navLinks": True,
}

# The calendar component returns a dictionary of the clicked event.
clicked_event = calendar(
    events=calendar_events,
    options=calendar_options,
    custom_css="""
        .fc-event-past { opacity: 0.7; }
        .fc-event-title { font-weight: 700; }
        .fc-toolbar-title { font-size: 1.5rem; }
    """,
    key="appointment_calendar"
)

# If an event is clicked, set the app to edit mode.
if clicked_event and clicked_event.get("event"):
    clicked_app_id = int(clicked_event["event"]["extendedProps"]["id"])
    # Avoid re-triggering on the same click
    if st.session_state.get('edit_app_id') != clicked_app_id:
        st.session_state.edit_mode_app = True
        st.session_state.edit_app_id = clicked_app_id
        st.rerun()

# --- 2. FORM TO ADD/EDIT APPOINTMENT ---
st.markdown("---")
is_edit_mode = st.session_state.get('edit_mode_app', False)
expander_title = "✏️ Edit Selected Appointment" if is_edit_mode else "➕ Add New Appointment"

with st.expander(expander_title, expanded=is_edit_mode):
    with st.container(border=True):
        edit_app_id = st.session_state.get('edit_app_id')
        default_values = {}
        # Pre-fill the form if in edit mode
        if is_edit_mode and edit_app_id:
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
            doctor_name = st.text_input("Doctor's Name / Hospital", value=default_values.get('doctor_name', ''))
            purpose = st.text_input("Purpose of Visit", value=default_values.get('purpose', ''))
            location = st.text_input("Location / Address", value=default_values.get('location', ''))

            col1, col2 = st.columns(2)
            with col1:
                app_date = st.date_input("Date", value=default_values.get('date', datetime.now().date()))
            with col2:
                app_time = st.time_input("Time", value=default_values.get('time', datetime.now().time()))

            # --- Form Buttons ---
            b_col1, b_col2, b_col3, b_col4 = st.columns([3, 1, 1, 2])
            with b_col1:
                save_button = st.form_submit_button("💾 Save Appointment", type="primary", use_container_width=True)
            if is_edit_mode:
                with b_col2:
                    delete_button = st.form_submit_button("🗑️ Delete", use_container_width=True)
                with b_col3:
                    cancel_button = st.form_submit_button("✖️ Cancel", use_container_width=True)
            else:
                delete_button = cancel_button = False

            # --- Form Submission Logic ---
            if save_button:
                if not doctor_name:
                    st.warning("Doctor's Name is a required field.")
                else:
                    app_data = {
                        "doctor_name": doctor_name.strip(),
                        "purpose": purpose.strip(),
                        "location": location.strip(),
                        "appointment_datetime": datetime.combine(app_date, app_time).isoformat()
                    }
                    if is_edit_mode:
                        response = api.put(f"/appointments/{st.session_state.edit_app_id}", json_data=app_data)
                        if response:
                            st.toast("Appointment updated successfully!", icon="✅")
                    else:
                        response = api.post("/appointments/", json_data=app_data)
                        if response:
                            st.toast("New appointment added!", icon="🎉")

                    # If the API call was successful, reset state and refresh data
                    if response:
                        st.session_state.edit_mode_app = False
                        st.session_state.pop('edit_app_id', None)
                        fetch_appointments()
                        st.rerun()

            if delete_button:
                response = api.delete(f"/appointments/{st.session_state.edit_app_id}")
                if response:
                    st.toast("Appointment deleted.", icon="🗑️")
                    st.session_state.edit_mode_app = False
                    st.session_state.pop('edit_app_id', None)
                    fetch_appointments()
                    st.rerun()

            if cancel_button:
                st.session_state.edit_mode_app = False
                st.session_state.pop('edit_app_id', None)
                st.rerun()
