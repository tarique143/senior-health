# frontend/pages/Medications.py (Corrected Version)

import streamlit as st
import requests
import os
from datetime import datetime

# --- CONFIGURATION & API CLIENT ---
st.set_page_config(page_title="My Medications", layout="wide")

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
def fetch_medications():
    """API se dawaiyan fetch karke session state mein save karta hai."""
    response = api.get("/medications/")
    if response and response.status_code == 200:
        st.session_state.medications = sorted(response.json(), key=lambda x: datetime.strptime(x['timing'], '%H:%M:%S').time())
    else:
        st.session_state.medications = []
        st.error("Could not fetch medications.")

# --- INITIAL DATA FETCH ---
if 'medications' not in st.session_state:
    fetch_medications()

# --- PAGE CONTENT ---

st.header("💊 My Medications")
st.write("Manage your daily medication schedule here.")
st.markdown("---")

# --- FORM TO ADD/EDIT MEDICATION ---
with st.expander("**➕ Add New Medication** or select one below to edit", expanded=st.session_state.get('edit_mode', False)):
    
    edit_med_id = st.session_state.get('edit_med_id')
    default_values = {}
    if edit_med_id and 'medications' in st.session_state:
        med_to_edit = next((m for m in st.session_state.medications if m['id'] == edit_med_id), None)
        if med_to_edit:
            default_values = {
                "name": med_to_edit.get('name', ''),
                "dosage": med_to_edit.get('dosage', ''),
                "timing": datetime.strptime(med_to_edit.get('timing', '08:00:00'), '%H:%M:%S').time(),
                "is_active": med_to_edit.get('is_active', True)
            }

    with st.form("med_form", clear_on_submit=True):
        name = st.text_input("Medication Name", value=default_values.get('name', ''))
        dosage = st.text_input("Dosage (e.g., '1 tablet', '10mg')", value=default_values.get('dosage', ''))
        timing = st.time_input("Time to Take", value=default_values.get('timing', datetime.now().time()))
        is_active = st.checkbox("Medication is currently active", value=default_values.get('is_active', True))
        
        submitted = st.form_submit_button(
            "Update Medication" if st.session_state.get('edit_mode') else "Add Medication", 
            type="primary"
        )

        if submitted:
            med_data = {
                "name": name,
                "dosage": dosage,
                "timing": timing.strftime('%H:%M:%S'),
                "is_active": is_active
            }
            if st.session_state.get('edit_mode'):
                response = api.put(f"/medications/{st.session_state.edit_med_id}", json=med_data)
                if response and response.status_code == 200:
                    st.toast("Medication updated!", icon="✅")
                else:
                    st.error("Failed to update medication.")
            else:
                response = api.post("/medications/", json=med_data)
                if response and response.status_code == 201:
                    st.toast("Medication added!", icon="🎉")
                else:
                    st.error("Failed to add medication.")
            
            st.session_state.edit_mode = False
            st.session_state.pop('edit_med_id', None)
            fetch_medications()
            st.rerun()

# --- DISPLAY MEDICATIONS LIST ---

st.subheader("Your Schedule")

if not st.session_state.medications:
    st.info("You haven't added any medications yet. Use the form above to add your first one.")
else:
    for med in st.session_state.medications:
        med_time = datetime.strptime(med['timing'], '%H:%M:%S').strftime('%I:%M %p')
        status = "🟢 Active" if med['is_active'] else "🔴 Inactive"
        
        with st.container(border=True):
            col1, col2, col3 = st.columns([4, 2, 1.5])
            with col1:
                st.markdown(f"#### {med['name']}")
                st.write(f"**Dosage:** {med['dosage']}")
            with col2:
                st.markdown(f"**Time:** `{med_time}`")
                st.write(f"**Status:** {status}")
            
            with col3:
                if st.button("Edit", key=f"edit_{med['id']}", use_container_width=True):
                    st.session_state.edit_mode = True
                    st.session_state.edit_med_id = med['id']
                    st.rerun()

                if st.button("Delete", key=f"delete_{med['id']}", type="secondary", use_container_width=True):
                    with st.spinner("Deleting..."):
                        response = api.delete(f"/medications/{med['id']}")
                    if response and response.status_code == 204:
                        st.toast(f"{med['name']} deleted.", icon="🗑️")
                        fetch_medications()
                        st.rerun()
                    else:
                        st.error("Failed to delete.")

if st.session_state.get('edit_mode') and st.button("Cancel Edit"):
    st.session_state.edit_mode = False
    st.session_state.pop('edit_med_id', None)
    st.rerun()
