# /frontend/pages/Contacts.py

import os

import requests
import streamlit as st

# --- 1. PAGE CONFIGURATION ---
# KEY CHANGE: This is now the first Streamlit command in the script.
st.set_page_config(page_title="Emergency Contacts", layout="wide", icon="🆘")

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
            error_detail = e.response.json().get('detail', 'An unknown API error occurred.')
            st.error(f"Error: {error_detail}")
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
def fetch_contacts():
    """Fetches contacts from the API and stores them in the session state."""
    response = api.get("/contacts/")
    st.session_state.contacts = response.json() if response and response.status_code == 200 else []

# --- Initial Data Fetch ---
if 'contacts' not in st.session_state:
    with st.spinner("Loading your contacts..."):
        fetch_contacts()

# --- Main Page Content ---
st.header("🆘 Emergency Contacts")
st.write(
    "Manage your important contacts here. "
    "The **first contact** in the list is automatically used as your primary SOS contact."
)
st.markdown("---")

# --- 1. FORM TO ADD/EDIT CONTACT ---
is_edit_mode = st.session_state.get('edit_mode_contact', False)
expander_title = "✏️ Edit Selected Contact" if is_edit_mode else "➕ Add New Contact"

with st.expander(expander_title, expanded=is_edit_mode or len(st.session_state.get('contacts', [])) < 5):
    with st.container(border=True):
        edit_contact_id = st.session_state.get('edit_contact_id')
        default_values = {}
        if is_edit_mode and edit_contact_id:
            contact_to_edit = next((c for c in st.session_state.contacts if c['id'] == edit_contact_id), None)
            if contact_to_edit:
                default_values = {
                    "name": contact_to_edit.get('name', ''),
                    "phone_number": contact_to_edit.get('phone_number', ''),
                    "relationship_type": contact_to_edit.get('relationship_type', '')
                }

        with st.form("contact_form", clear_on_submit=False):
            name = st.text_input("Contact Name*", value=default_values.get('name', ''))
            phone_number = st.text_input("Phone Number*", value=default_values.get('phone_number', ''))
            relationship_type = st.text_input("Relationship (e.g., Son, Doctor)", value=default_values.get('relationship_type', ''))

            b_col1, b_col2, b_col3 = st.columns([2, 1, 3])
            with b_col1:
                save_button = st.form_submit_button("💾 Save Contact", type="primary", use_container_width=True)
            if is_edit_mode:
                with b_col2:
                    cancel_button = st.form_submit_button("✖️ Cancel", use_container_width=True)
            else:
                cancel_button = False

            if save_button:
                if not name or not phone_number:
                    st.warning("Name and Phone Number are required fields.")
                else:
                    contact_data = {
                        "name": name.strip(),
                        "phone_number": phone_number.strip(),
                        "relationship_type": relationship_type.strip()
                    }
                    if is_edit_mode:
                        response = api.put(f"/contacts/{st.session_state.edit_contact_id}", json_data=contact_data)
                        if response: st.toast("Contact updated successfully!", icon="✅")
                    else:
                        response = api.post("/contacts/", json_data=contact_data)
                        if response: st.toast("New contact added!", icon="🎉")

                    if response:
                        st.session_state.edit_mode_contact = False
                        st.session_state.pop('edit_contact_id', None)
                        fetch_contacts()
                        st.rerun()

            if cancel_button:
                st.session_state.edit_mode_contact = False
                st.session_state.pop('edit_contact_id', None)
                st.rerun()

# --- 2. DISPLAY CONTACTS LIST ---
st.subheader("Your Saved Contacts")

contacts = st.session_state.get('contacts', [])
if not contacts:
    st.info("You have no emergency contacts saved yet. Use the form above to add one.")
else:
    cols = st.columns(3)
    for i, contact in enumerate(contacts):
        with cols[i % 3]:
            with st.container(border=True):
                if i == 0:
                    st.markdown(f"#### {contact['name']} ⭐")
                    st.caption("Primary SOS Contact")
                else:
                    st.markdown(f"#### {contact['name']}")

                st.markdown(f"*{contact.get('relationship_type', 'Contact')}*")
                st.markdown(f"<h3>📞 {contact['phone_number']}</h3>", unsafe_allow_html=True)

                b_col1, b_col2 = st.columns(2)
                with b_col1:
                    if st.button("Edit", key=f"edit_c_{contact['id']}", use_container_width=True):
                        st.session_state.edit_mode_contact = True
                        st.session_state.edit_contact_id = contact['id']
                        st.rerun()
                with b_col2:
                    if st.button("Delete", key=f"delete_c_{contact['id']}", type="secondary", use_container_width=True):
                        response = api.delete(f"/contacts/{contact['id']}")
                        if response:
                            st.toast(f"Contact '{contact['name']}' has been deleted.", icon="🗑️")
                            fetch_contacts()
                            st.rerun()
