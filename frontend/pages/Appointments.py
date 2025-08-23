# frontend/pages/Appointments.py (Corrected Version)

import streamlit as st
import requests
import os
from datetime import datetime

# --- CONFIGURATION & API CLIENT ---
st.set_page_config(page_title="My Appointments", layout="wide")

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

class ApiClient:
    def __init__(self, base_url):
        self.base_url = base_url
    def _get_headers(self):
        ### <<< CHANGE HERE
        token = st.session_state.get("access_token")
        if not token:
            st.warning("Please login first.")
            st.switch_page("streamlit_app.py")
            st.stop()
        return {"Authorization": f"Bearer {token}"}
    def _make_request(self, method, endpoint, **kwargs):
        try:
            return requests.request(method, f"{self.base_url}{endpoint}", headers=self._get_headers(), timeout=10, **kwargs)
        except requests.exceptions.RequestException:
            st.error("Connection Error: Could not connect to the backend server."); return None
    def get(self, endpoint): return self._make_request("GET", endpoint)
    def post(self, endpoint, json=None): return self._make_request("POST", endpoint, json=json)
    def put(self, endpoint, json=None): return self._make_request("PUT", endpoint, json=json)
    def delete(self, endpoint): return self._make_request("DELETE", endpoint)

api = ApiClient(API_BASE_URL)

# --- SECURITY CHECK ---
### <<< CHANGE HERE
if 'access_token' not in st.session_state:
    st.warning("Please login first to access this page.")
    st.switch_page("streamlit_app.py")
    st.stop()

# --- HELPER FUNCTIONS ---
def fetch_appointments():
    """API se appointments fetch karke session state mein save karta hai."""
    response = api.get("/appointments/")
    if response and response.status_code == 200:
        # Appointments ko date ke hisab se sort karein
        st.session_state.appointments = sorted(response.json(), key=lambda x: x['appointment_datetime'])
    else:
        st.session_state.appointments = []
        st.error("Could not fetch appointments.")

# --- INITIAL DATA FETCH ---
if 'appointments' not in st.session_state:
    fetch_appointments()

# --- PAGE CONTENT ---
st.header("🗓️ My Appointments")
st.write("Keep track of your doctor visits and medical check-ups.")
st.markdown("---")

# --- FORM TO ADD/EDIT APPOINTMENT ---
with st.expander("**➕ Add New Appointment** or select one below to edit", expanded=st.session_state.get('edit_mode_app', False)):
    
    # Edit mode ke liye default values set karein
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

    with st.form("app_form", clear_on_submit=True):
        doctor_name = st.text_input("Doctor's Name / Hospital", value=default_values.get('doctor_name', ''))
        purpose = st.text_input("Purpose of Visit", value=default_values.get('purpose', ''))
        location = st.text_input("Location / Address", value=default_values.get('location', ''))
        
        col1, col2 = st.columns(2)
        with col1:
            app_date = st.date_input("Date", value=default_values.get('date', datetime.now().date()))
        with col2:
            app_time = st.time_input("Time", value=default_values.get('time', datetime.now().time()))
        
        submitted = st.form_submit_button(
            "Update Appointment" if st.session_state.get('edit_mode_app') else "Add Appointment",
            type="primary"
        )

        if submitted:
            # Combine date and time
            appointment_datetime = datetime.combine(app_date, app_time).isoformat()
            
            app_data = {
                "doctor_name": doctor_name,
                "purpose": purpose,
                "location": location,
                "appointment_datetime": appointment_datetime
            }
            if st.session_state.get('edit_mode_app'):
                # Update logic
                response = api.put(f"/appointments/{st.session_state.edit_app_id}", json=app_data)
                if response and response.status_code == 200:
                    st.toast("Appointment updated!", icon="✅")
                else:
                    st.error("Failed to update appointment.")
            else:
                # Add logic
                response = api.post("/appointments/", json=app_data)
                if response and response.status_code == 201:
                    st.toast("Appointment added!", icon="🎉")
                else:
                    st.error("Failed to add appointment.")
            
            st.session_state.edit_mode_app = False
            st.session_state.pop('edit_app_id', None)
            fetch_appointments()
            st.rerun()

# --- DISPLAY APPOINTMENTS LIST ---
st.subheader("Upcoming Schedule")

if not st.session_state.appointments:
    st.info("You have no appointments scheduled. Use the form above to add one.")
else:
    # Separate past and upcoming appointments
    now = datetime.now()
    upcoming_apps = [app for app in st.session_state.appointments if datetime.fromisoformat(app['appointment_datetime']) >= now]
    past_apps = [app for app in st.session_state.appointments if datetime.fromisoformat(app['appointment_datetime']) < now]

    if upcoming_apps:
        for app in upcoming_apps:
            dt_obj = datetime.fromisoformat(app['appointment_datetime'])
            app_date_str = dt_obj.strftime("%A, %B %d, %Y")
            app_time_str = dt_obj.strftime('%I:%M %p')

            with st.container(border=True):
                col1, col2, col3 = st.columns([4, 2, 1.5])
                with col1:
                    st.markdown(f"#### Dr. {app['doctor_name']}")
                    st.write(f"**Purpose:** {app.get('purpose', 'N/A')}")
                with col2:
                    st.write(f"**Date:** `{app_date_str}`")
                    st.write(f"**Time:** `{app_time_str}`")
                with col3:
                    if st.button("Edit", key=f"edit_app_{app['id']}", use_container_width=True):
                        st.session_state.edit_mode_app = True
                        st.session_state.edit_app_id = app['id']
                        st.rerun()
                    if st.button("Delete", key=f"delete_app_{app['id']}", type="secondary", use_container_width=True):
                        response = api.delete(f"/appointments/{app['id']}")
                        if response and response.status_code == 204:
                            st.toast("Appointment deleted.", icon="🗑️")
                            fetch_appointments()
                            st.rerun()
                        else: st.error("Failed to delete.")
    else:
        st.success("You have no upcoming appointments!")

    if past_apps:
        with st.expander("View Past Appointments"):
            for app in reversed(past_apps): # Show most recent first
                dt_obj = datetime.fromisoformat(app['appointment_datetime'])
                st.info(f"**{dt_obj.strftime('%d-%b-%Y')}**: Dr. {app['doctor_name']} for {app.get('purpose', 'a check-up')}.")

if st.session_state.get('edit_mode_app') and st.button("Cancel Edit"):
    st.session_state.edit_mode_app = False
    st.session_state.pop('edit_app_id', None)
    st.rerun()
