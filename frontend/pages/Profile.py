# frontend/pages/5_Profile.py

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
st.set_page_config(page_title="My Profile", layout="wide")

# --- PROFILE PAGE CONTENT ---

st.header("My Profile")

response = api.get("/users/me")
if not response or response.status_code != 200:
    st.error("Could not fetch your profile data. Please try logging in again.")
    st.stop()

user_data = response.json()

# Create two columns for a cleaner layout
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("Update Your Information")
        with st.form("update_profile_form"):
            full_name = st.text_input("Full Name", value=user_data.get('full_name', ''))
            
            # Handle date of birth safely
            dob_val = user_data.get('date_of_birth')
            try:
                dob_default = datetime.fromisoformat(dob_val).date() if dob_val else None
            except (TypeError, ValueError):
                dob_default = None # Default to None if date is invalid
            
            dob = st.date_input("Date of Birth", value=dob_default)
            address = st.text_area("Address", value=user_data.get('address', ''))
            
            if st.form_submit_button("Save Profile Changes"):
                update_data = {
                    "full_name": full_name,
                    "date_of_birth": dob.isoformat() if dob else None,
                    "address": address
                }
                update_response = api.put("/users/me", json=update_data)
                if update_response and update_response.status_code == 200:
                    st.success("Profile updated successfully!")
                    st.rerun()
                else:
                    st.error("Failed to update profile.")

with col2:
    with st.container(border=True):
        st.subheader("Change Your Password")
        with st.form("update_password_form", clear_on_submit=True):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_new_password = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("Change Password"):
                if not all([current_password, new_password, confirm_new_password]):
                    st.warning("Please fill in all password fields.")
                elif new_password != confirm_new_password:
                    st.error("New passwords do not match.")
                else:
                    pass_response = api.put("/users/me/password", json={
                        "current_password": current_password,
                        "new_password": new_password
                    })
                    if pass_response and pass_response.status_code == 200:
                        st.success("Password updated successfully!")
                    else:
                        error_detail = "An error occurred."
                        if pass_response:
                            try:
                                error_detail = pass_response.json().get('detail', error_detail)
                            except requests.exceptions.JSONDecodeError:
                                pass # Keep generic error if no JSON
                        st.error(f"Failed to update password: {error_detail}")

    with st.container(border=True):
        st.subheader("Delete Account")
        st.warning("DANGER ZONE: This action is permanent and cannot be undone. All your data will be erased.", icon="⚠️")
        
        if st.checkbox("I understand and wish to proceed with deleting my account."):
            if st.button("Delete My Account Permanently", type="primary"):
                delete_response = api.delete("/users/me")
                if delete_response and delete_response.status_code == 204:
                    st.toast("Account deleted successfully.")
                    # Clear session and force a rerun to the login page
                    st.session_state.clear()
                    st.rerun()
                else:
                    st.error("Could not delete account. Please try again.")