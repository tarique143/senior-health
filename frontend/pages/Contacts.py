# frontend/pages/Contacts.py (Nayi File)

import streamlit as st
import requests
import os

# --- CONFIGURATION & API CLIENT ---
st.set_page_config(page_title="Emergency Contacts", layout="wide")

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

class ApiClient:
    # (Pichli file se same ApiClient class yahan copy karein)
    def __init__(self, base_url):
        self.base_url = base_url
    def _get_headers(self):
        token = st.session_state.get("token")
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
if 'token' not in st.session_state:
    st.warning("Please login first to access this page.")
    st.switch_page("streamlit_app.py")
    st.stop()

# --- HELPER FUNCTIONS ---
def fetch_contacts():
    """API se contacts fetch karke session state mein save karta hai."""
    response = api.get("/contacts/")
    if response and response.status_code == 200:
        st.session_state.contacts = response.json()
    else:
        st.session_state.contacts = []
        st.error("Could not fetch contacts.")

# --- INITIAL DATA FETCH ---
if 'contacts' not in st.session_state:
    fetch_contacts()

# --- PAGE CONTENT ---
st.header("🆘 Emergency Contacts")
st.write("Manage your important contacts for quick access during emergencies.")
st.markdown("---")

# --- FORM TO ADD/EDIT CONTACT ---
with st.expander("**➕ Add New Contact** or select one below to edit", expanded=st.session_state.get('edit_mode_contact', False)):
    
    edit_contact_id = st.session_state.get('edit_contact_id')
    default_values = {}
    if edit_contact_id and 'contacts' in st.session_state:
        contact_to_edit = next((c for c in st.session_state.contacts if c['id'] == edit_contact_id), None)
        if contact_to_edit:
            default_values = {
                "name": contact_to_edit.get('name', ''),
                "phone_number": contact_to_edit.get('phone_number', ''),
                "relationship_type": contact_to_edit.get('relationship_type', '')
            }

    with st.form("contact_form", clear_on_submit=True):
        name = st.text_input("Contact Name", value=default_values.get('name', ''))
        phone_number = st.text_input("Phone Number", value=default_values.get('phone_number', ''))
        relationship_type = st.text_input("Relationship (e.g., Son, Doctor)", value=default_values.get('relationship_type', ''))
        
        submitted = st.form_submit_button(
            "Update Contact" if st.session_state.get('edit_mode_contact') else "Add Contact",
            type="primary"
        )

        if submitted:
            if not name or not phone_number:
                st.warning("Name and Phone Number are required.")
            else:
                contact_data = {
                    "name": name,
                    "phone_number": phone_number,
                    "relationship_type": relationship_type
                }
                if st.session_state.get('edit_mode_contact'):
                    response = api.put(f"/contacts/{st.session_state.edit_contact_id}", json=contact_data)
                    if response and response.status_code == 200:
                        st.toast("Contact updated!", icon="✅")
                    else:
                        st.error("Failed to update contact.")
                else:
                    response = api.post("/contacts/", json=contact_data)
                    if response and response.status_code == 201:
                        st.toast("Contact added!", icon="🎉")
                    else:
                        error_detail = "Failed to add contact. You may have reached the limit of 5 contacts."
                        if response:
                            try: error_detail = response.json().get('detail', error_detail)
                            except: pass
                        st.error(error_detail)

                st.session_state.edit_mode_contact = False
                st.session_state.pop('edit_contact_id', None)
                fetch_contacts()
                st.rerun()

# --- DISPLAY CONTACTS LIST ---
st.subheader("Your Saved Contacts")

if not st.session_state.contacts:
    st.info("You have no emergency contacts saved. Use the form above to add one.")
else:
    cols = st.columns(3) # Display up to 3 contacts per row
    col_index = 0
    for contact in st.session_state.contacts:
        with cols[col_index]:
            with st.container(border=True):
                st.markdown(f"#### {contact['name']}")
                st.markdown(f"*{contact.get('relationship_type', 'Contact')}*")
                st.subheader(f"📞 {contact['phone_number']}")
                
                b_col1, b_col2 = st.columns(2)
                with b_col1:
                    if st.button("Edit", key=f"edit_c_{contact['id']}", use_container_width=True):
                        st.session_state.edit_mode_contact = True
                        st.session_state.edit_contact_id = contact['id']
                        st.rerun()
                with b_col2:
                    if st.button("Delete", key=f"delete_c_{contact['id']}", type="secondary", use_container_width=True):
                        response = api.delete(f"/contacts/{contact['id']}")
                        if response and response.status_code == 204:
                            st.toast(f"{contact['name']} deleted.", icon="🗑️")
                            fetch_contacts()
                            st.rerun()
                        else: st.error("Failed to delete.")
        
        col_index = (col_index + 1) % 3


if st.session_state.get('edit_mode_contact') and st.button("Cancel Edit"):
    st.session_state.edit_mode_contact = False
    st.session_state.pop('edit_contact_id', None)
    st.rerun()
