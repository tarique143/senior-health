# frontend/pages/3_Appointments.py

import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURATION & API CLIENT (Required on every page) ---
API_BASE_URL = "http://127.0.0.1:8000"

class ApiClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = st.session_state.get("token", None)

    def _get_headers(self):
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

    def _make_request(self, method, endpoint, **kwargs):
        try:
            response = requests.request(method, f"{self.base_url}{endpoint}", headers=self._get_headers(), **kwargs)
            return response
        except requests.exceptions.ConnectionError:
            st.error("Connection Error: Could not connect to the backend server.")
            return None

    def post(self, endpoint, data=None, json=None):
        return self._make_request("POST", endpoint, data=data, json=json)
    def get(self, endpoint, params=None):
        return self._make_request("GET", endpoint, params=params)
    def put(self, endpoint, json=None):
        return self._make_request("PUT", endpoint, json=json)
    def delete(self, endpoint):
        return self._make_request("DELETE", endpoint)

api = ApiClient(API_BASE_URL)

# --- SECURITY CHECK (Required on every page) ---
if 'token' not in st.session_state:
    st.warning("Please login first to access this page.")
    st.stop()

# --- PAGE CONFIG ---
st.set_page_config(page_title="My Appointments", layout="wide")

# --- APPOINTMENTS PAGE CONTENT ---

st.header("My Appointments")

with st.expander("➕ Add New Appointment"):
    with st.form("new_app_form", clear_on_submit=True):
        doctor_name = st.text_input("Doctor's Name")
        purpose = st.text_input("Purpose of Visit")
        app_date = st.date_input("Appointment Date", min_value=datetime.today())
        app_time = st.time_input("Appointment Time")
        location = st.text_area("Clinic/Hospital Address")
        
        if st.form_submit_button("Add Appointment"):
            if not doctor_name:
                st.warning("Please enter the doctor's name.")
            else:
                app_datetime = datetime.combine(app_date, app_time)
                response = api.post("/appointments/", json={
                    "doctor_name": doctor_name,
                    "purpose": purpose,
                    "appointment_datetime": app_datetime.isoformat(),
                    "location": location
                })
                if response and response.status_code == 201:
                    st.success("Appointment added successfully!")
                    st.rerun()
                else:
                    st.error("Failed to add appointment.")

st.subheader("Your Appointment List")

response = api.get("/appointments/")
if response and response.status_code == 200:
    # Sort appointments with the most recent first
    apps = sorted(response.json(), key=lambda x: x['appointment_datetime'], reverse=True)
    
    if not apps:
        st.info("You have not added any appointments yet. Use the form above to get started.")

    for app in apps:
        with st.container(border=True):
            # Check if this specific appointment is being edited
            if st.session_state.get('editing_app_id') == app['id']:
                 with st.form(key=f"edit_app_form_{app['id']}"):
                    st.subheader(f"Editing Appointment")
                    app_dt_obj = datetime.fromisoformat(app['appointment_datetime'])

                    new_doctor = st.text_input("Doctor's Name", value=app['doctor_name'])
                    new_purpose = st.text_input("Purpose", value=app.get('purpose', ''))
                    new_date = st.date_input("Date", value=app_dt_obj.date(), min_value=datetime.today())
                    new_time = st.time_input("Time", value=app_dt_obj.time())
                    new_location = st.text_area("Location", value=app.get('location', ''))
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.form_submit_button("Save Changes"):
                            new_datetime = datetime.combine(new_date, new_time)
                            update_data = {
                                "doctor_name": new_doctor,
                                "purpose": new_purpose,
                                "appointment_datetime": new_datetime.isoformat(),
                                "location": new_location
                            }
                            put_response = api.put(f"/appointments/{app['id']}", json=update_data)
                            if put_response and put_response.status_code == 200:
                                st.success("Appointment updated!")
                                del st.session_state['editing_app_id']
                                st.rerun()
                            else:
                                st.error("Failed to update appointment.")
                    with c2:
                        if st.form_submit_button("Cancel", type="secondary"):
                            del st.session_state['editing_app_id']
                            st.rerun()
            else:
                # Default view: Display the appointment info
                c1, c2, c3 = st.columns([4, 1, 1])
                app_dt = datetime.fromisoformat(app['appointment_datetime'])
                with c1:
                    st.write(f"**{app['doctor_name']}** on **{app_dt.strftime('%d %b %Y, %I:%M %p')}**")
                    st.caption(f"Purpose: {app.get('purpose', 'N/A')} | Location: {app.get('location', 'N/A')}")
                with c2:
                    if st.button("Edit", key=f"edit_app_{app['id']}"):
                        st.session_state['editing_app_id'] = app['id']
                        st.rerun()
                with c3:
                    if st.button("Delete", type="secondary", key=f"del_app_{app['id']}"):
                        delete_response = api.delete(f"/appointments/{app['id']}")
                        if delete_response and delete_response.status_code == 204:
                            st.toast("Appointment deleted.")
                            st.rerun()
                        else:
                            st.error("Failed to delete appointment.")
else:
    st.error("Could not load your appointment data from the server.")