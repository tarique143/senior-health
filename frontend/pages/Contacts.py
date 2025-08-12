# frontend/pages/4_Contacts.py

import streamlit as st
import requests

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

# --- PAGE CONFIG AND STYLES ---
st.set_page_config(page_title="Emergency Contacts", layout="wide")

st.markdown("""
    <style>
        .call-link {
            display: block; padding: 12px; background-color: #fce4e4;
            border-radius: 8px; text-align: center; text-decoration: none;
            color: #c92a2a; font-weight: bold; margin-bottom: 10px; border: 1px solid #ffc9c9;
        }
        .call-link:hover { background-color: #ffc9c9; color: #a71c1c; }
    </style>
""", unsafe_allow_html=True)


# --- CONTACTS PAGE CONTENT ---

st.header("Emergency Contacts")

with st.expander("➕ Add New Contact"):
    with st.form("new_contact_form", clear_on_submit=True):
        name = st.text_input("Contact's Name")
        phone_number = st.text_input("Phone Number")
        relationship_type = st.text_input("Relationship (e.g., 'Son', 'Doctor', 'Neighbor')")
        
        if st.form_submit_button("Add Contact"):
            if not name or not phone_number:
                st.warning("Please provide the contact's name and phone number.")
            else:
                response = api.post("/contacts/", json={
                    "name": name,
                    "phone_number": phone_number,
                    "relationship_type": relationship_type
                })
                if response and response.status_code == 201:
                    st.success("Contact added successfully!")
                    st.rerun()
                elif response and response.status_code == 400:
                    st.error(response.json().get('detail'))
                else:
                    st.error("Failed to add contact.")

st.subheader("Your Contact List")

response = api.get("/contacts/")
if response and response.status_code == 200:
    contacts = response.json()
    
    if not contacts:
        st.info("You have not added any emergency contacts yet. Use the form above to get started.")

    # Create two columns for a better layout on larger screens
    col1, col2 = st.columns(2)
    
    for i, contact in enumerate(contacts):
        # Alternate between columns
        current_col = col1 if i % 2 == 0 else col2
        
        with current_col:
            with st.container(border=True):
                # Check if this specific contact is being edited
                if st.session_state.get('editing_contact_id') == contact['id']:
                    with st.form(key=f"edit_contact_form_{contact['id']}"):
                        st.subheader(f"Editing: {contact['name']}")
                        new_name = st.text_input("Name", value=contact['name'])
                        new_phone = st.text_input("Phone Number", value=contact['phone_number'])
                        new_relationship = st.text_input("Relationship", value=contact.get('relationship_type', ''))
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.form_submit_button("Save Changes"):
                                update_data = {"name": new_name, "phone_number": new_phone, "relationship_type": new_relationship}
                                put_response = api.put(f"/contacts/{contact['id']}", json=update_data)
                                if put_response and put_response.status_code == 200:
                                    st.success("Contact updated!")
                                    del st.session_state['editing_contact_id']
                                    st.rerun()
                                else:
                                    st.error("Failed to update contact.")
                        with c2:
                            if st.form_submit_button("Cancel", type="secondary"):
                                del st.session_state['editing_contact_id']
                                st.rerun()
                else:
                    # Default view: Display the contact info and quick dial link
                    phone_num = contact['phone_number']
                    st.markdown(f"**{contact['name']}** ({contact.get('relationship_type', 'N/A')})")
                    
                    # Clickable "Call" link
                    st.markdown(f'<a href="tel:{phone_num}" class="call-link">Call {phone_num}</a>', unsafe_allow_html=True)
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Edit", key=f"edit_contact_{contact['id']}", use_container_width=True):
                            st.session_state['editing_contact_id'] = contact['id']
                            st.rerun()
                    with c2:
                        if st.button("Delete", type="secondary", key=f"del_contact_{contact['id']}", use_container_width=True):
                            delete_response = api.delete(f"/contacts/{contact['id']}")
                            if delete_response and delete_response.status_code == 204:
                                st.toast("Contact deleted.")
                                st.rerun()
                            else:
                                st.error("Failed to delete contact.")
else:
    st.error("Could not load your contact data from the server.")