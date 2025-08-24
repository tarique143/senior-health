# /frontend/pages/Medications.py

import os
from datetime import datetime

import requests
import streamlit as st

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="My Medications", layout="wide", icon="💊")

# --- 2. Custom UI Components ---
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
            st.switch_page("streamlit_app.py")
            st.stop()
        return {"Authorization": f"Bearer {token}"}

    def _make_request(self, method: str, endpoint: str, **kwargs):
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method, url, headers=self._get_headers(), timeout=15, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            st.error(f"API Error: {e.response.json().get('detail', 'Unknown error')}")
        except requests.exceptions.ConnectionError:
            st.error("Connection Error: Could not connect to the server.")
        return None

    def get(self, endpoint: str): return self._make_request("GET", endpoint)
    def post(self, endpoint: str, json_data: dict): return self._make_request("POST", endpoint, json=json_data)
    def put(self, endpoint: str, json_data: dict): return self._make_request("PUT", endpoint, json=json_data)
    def delete(self, endpoint: str): return self._make_request("DELETE", endpoint)

api = ApiClient(API_BASE_URL)

# --- Security Check ---
if 'access_token' not in st.session_state:
    st.warning("Please login first to access this page.")
    st.switch_page("streamlit_app.py")
    st.stop()


# --- Helper Function ---
def fetch_medications():
    """Fetches medications from the API and stores them in the session state."""
    response = api.get("/medications/")
    if response and response.status_code == 200:
        # Sort medications by time for a chronological schedule.
        st.session_state.medications = sorted(
            response.json(), key=lambda x: datetime.strptime(x['timing'], '%H:%M:%S').time()
        )
    else:
        st.session_state.medications = []

# --- Initial Data Fetch ---
if 'medications' not in st.session_state:
    with st.spinner("Loading your medications..."):
        fetch_medications()


# --- Main Page Content ---
st.header("💊 My Medications")
st.write("Manage your daily medication schedule here. Add new medications or edit existing ones.")
st.markdown("---")

# --- 1. FORM TO ADD/EDIT MEDICATION ---
is_edit_mode = st.session_state.get('edit_mode_med', False)
expander_title = "✏️ Edit Selected Medication" if is_edit_mode else "➕ Add New Medication"

with st.expander(expander_title, expanded=is_edit_mode or not st.session_state.get('medications')):
    with st.container(border=True):
        edit_med_id = st.session_state.get('edit_med_id')
        default_values = {}
        if is_edit_mode and edit_med_id:
            med_to_edit = next((m for m in st.session_state.medications if m['id'] == edit_med_id), None)
            if med_to_edit:
                default_values = {
                    "name": med_to_edit.get('name', ''),
                    "dosage": med_to_edit.get('dosage', ''),
                    "timing": datetime.strptime(med_to_edit.get('timing', '08:00:00'), '%H:%M:%S').time(),
                    "is_active": med_to_edit.get('is_active', True)
                }

        with st.form("med_form", clear_on_submit=False):
            name = st.text_input("Medication Name*", value=default_values.get('name', ''))
            dosage = st.text_input("Dosage* (e.g., '1 tablet', '10mg')", value=default_values.get('dosage', ''))
            timing = st.time_input("Time to Take*", value=default_values.get('timing', datetime.now().time()))
            is_active = st.checkbox("This medication is currently active", value=default_values.get('is_active', True))

            b_col1, b_col2, b_col3 = st.columns([2, 1, 3])
            with b_col1:
                save_button = st.form_submit_button("💾 Save Medication", type="primary", use_container_width=True)
            if is_edit_mode:
                with b_col2:
                    cancel_button = st.form_submit_button("✖️ Cancel", use_container_width=True)
            else:
                cancel_button = False

            if save_button:
                if not name or not dosage:
                    st.warning("Name and Dosage are required fields.")
                else:
                    med_data = {
                        "name": name.strip(),
                        "dosage": dosage.strip(),
                        "timing": timing.strftime('%H:%M:%S'),
                        "is_active": is_active
                    }
                    if is_edit_mode:
                        response = api.put(f"/medications/{st.session_state.edit_med_id}", json_data=med_data)
                        if response: st.toast("Medication updated successfully!", icon="✅")
                    else:
                        response = api.post("/medications/", json_data=med_data)
                        if response: st.toast("New medication added!", icon="🎉")

                    if response:
                        st.session_state.edit_mode_med = False
                        st.session_state.pop('edit_med_id', None)
                        fetch_medications()
                        st.rerun()

            if cancel_button:
                st.session_state.edit_mode_med = False
                st.session_state.pop('edit_med_id', None)
                st.rerun()

# --- 2. DISPLAY MEDICATIONS LIST ---
st.subheader("Your Medication Schedule")

medications = st.session_state.get('medications', [])
if not medications:
    st.info("You haven't added any medications yet. Use the form above to get started.")
else:
    for med in medications:
        with st.container(border=True):
            col1, col2, col3 = st.columns([4, 2, 1.5])
            with col1:
                st.markdown(f"#### {med['name']}")
                st.write(f"**Dosage:** {med['dosage']}")
            with col2:
                med_time = datetime.strptime(med['timing'], '%H:%M:%S').strftime('%I:%M %p')
                status_text = "🟢 Active" if med['is_active'] else "🔴 Inactive"
                st.markdown(f"**Time:** `{med_time}`")
                st.write(f"**Status:** {status_text}")
            with col3:
                if st.button("Edit", key=f"edit_{med['id']}", use_container_width=True):
                    st.session_state.edit_mode_med = True
                    st.session_state.edit_med_id = med['id']
                    st.rerun()
                if st.button("Delete", key=f"delete_{med['id']}", type="secondary", use_container_width=True):
                    response = api.delete(f"/medications/{med['id']}")
                    if response:
                        st.toast(f"Medication '{med['name']}' was deleted.", icon="🗑️")
                        fetch_medications()
                        st.rerun()
