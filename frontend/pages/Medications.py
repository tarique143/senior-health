# frontend/pages/2_Medications.py

import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURATION & API CLIENT (Required on every page) ---
if "API_BASE_URL" in st.secrets:
    API_BASE_URL = st.secrets["API_BASE_URL"]
else:
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
st.set_page_config(page_title="My Medications", layout="wide")

# --- MEDICATION PAGE CONTENT ---

st.header("My Medications")

with st.expander("➕ Add New Medication"):
    with st.form("new_med_form", clear_on_submit=True):
        name = st.text_input("Medication Name")
        dosage = st.text_input("Dosage (e.g., '1 tablet', '5 ml')")
        timing = st.time_input("Time to Take")
        
        if st.form_submit_button("Add Medication"):
            if not name or not dosage:
                st.warning("Please provide a name and dosage for the medication.")
            else:
                response = api.post("/medications/", json={"name": name, "dosage": dosage, "timing": timing.strftime("%H:%M:%S")})
                if response and response.status_code == 201:
                    st.success("Medication added successfully!")
                    st.rerun()
                else:
                    st.error("Failed to add medication.")

st.subheader("Your Medication List")

response = api.get("/medications/")
if response and response.status_code == 200:
    meds = sorted(response.json(), key=lambda x: datetime.strptime(x['timing'], '%H:%M:%S').time())
    if not meds:
        st.info("You have not added any medications yet. Use the form above to get started.")
        
    for med in meds:
        with st.container(border=True):
            # Check if this specific medication is being edited
            if st.session_state.get('editing_med_id') == med['id']:
                with st.form(key=f"edit_form_{med['id']}"):
                    st.subheader(f"Editing: {med['name']}")
                    
                    # Form fields pre-filled with existing data
                    new_name = st.text_input("Name", value=med['name'])
                    new_dosage = st.text_input("Dosage", value=med['dosage'])
                    new_timing_dt = datetime.strptime(med['timing'], '%H:%M:%S').time()
                    new_timing = st.time_input("Time", value=new_timing_dt)
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.form_submit_button("Save Changes"):
                            update_data = {"name": new_name, "dosage": new_dosage, "timing": new_timing.strftime("%H:%M:%S")}
                            put_response = api.put(f"/medications/{med['id']}", json=update_data)
                            if put_response and put_response.status_code == 200:
                                st.success("Medication updated!")
                                del st.session_state['editing_med_id'] # Exit edit mode
                                st.rerun()
                            else:
                                st.error("Failed to update medication.")
                    with c2:
                        if st.form_submit_button("Cancel", type="secondary"):
                            del st.session_state['editing_med_id'] # Exit edit mode
                            st.rerun()
            else:
                # Default view: Display the medication info
                c1, c2, c3 = st.columns([4, 1, 1])
                with c1:
                    st.write(f"**{med['name']}** - {med['dosage']} at {datetime.strptime(med['timing'], '%H:%M:%S').strftime('%I:%M %p')}")
                with c2:
                    if st.button("Edit", key=f"edit_med_{med['id']}"):
                        st.session_state['editing_med_id'] = med['id'] # Enter edit mode
                        st.rerun()
                with c3:
                    if st.button("Delete", type="secondary", key=f"del_med_{med['id']}"):
                        delete_response = api.delete(f"/medications/{med['id']}")
                        if delete_response and delete_response.status_code == 204:
                            st.toast("Medication deleted.")
                            st.rerun()
                        else:
                            st.error("Failed to delete medication.")
else:
    st.error("Could not load your medication data from the server.")