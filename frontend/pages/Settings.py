# /frontend/pages/Settings.py

import os
from datetime import datetime

import requests
import streamlit as st

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Settings", layout="wide", icon="⚙️")

# --- 2. Custom UI Components ---
from ui_components import apply_styles, build_sidebar

# --- 3. APPLY STYLES & SIDEBAR ---
apply_styles()
build_sidebar()

# --- 4. API & SESSION STATE SETUP ---
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

class ApiClient:
    """A client to interact with the backend, with special handling for file uploads."""
    def __init__(self, base_url: str):
        self.base_url = base_url

    def _get_headers(self, is_json: bool = True) -> dict:
        token = st.session_state.get("access_token")
        if not token:
            st.warning("Your session has expired. Please login again.")
            st.switch_page("streamlit_app.py")
            st.stop()
        headers = {"Authorization": f"Bearer {token}"}
        if is_json:
            headers["Content-Type"] = "application/json"
        return headers

    def _make_request(self, method: str, endpoint: str, **kwargs):
        url = f"{self.base_url}{endpoint}"
        try:
            is_json = "files" not in kwargs
            response = requests.request(method, url, headers=self._get_headers(is_json), timeout=20, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            error_detail = e.response.json().get('detail', 'An unknown API error occurred.')
            st.error(f"Error: {error_detail}")
        except requests.exceptions.ConnectionError:
            st.error("Connection Error: Could not connect to the server.")
        return None

    def get(self, endpoint: str): return self._make_request("GET", endpoint)
    def put(self, endpoint: str, json_data: dict): return self._make_request("PUT", endpoint, json=json_data)
    def post_files(self, endpoint: str, files: dict): return self._make_request("POST", endpoint, files=files)

api = ApiClient(API_BASE_URL)

# --- Security Check ---
if 'access_token' not in st.session_state:
    st.warning("Please login first to access this page.")
    st.switch_page("streamlit_app.py")
    st.stop()


# --- Helper Function ---
def fetch_user_profile():
    """Fetches the user's profile data from the API."""
    response = api.get("/users/me")
    if response and response.status_code == 200:
        st.session_state.user_profile = response.json()
    else:
        st.error("Could not load your profile. Please try logging in again.")
        st.session_state.clear()
        st.switch_page("streamlit_app.py")
        st.stop()

# --- Initial Data Fetch ---
if 'user_profile' not in st.session_state:
    with st.spinner("Loading your profile..."):
        fetch_user_profile()

profile = st.session_state.user_profile

# --- Main Page Content ---
st.header("⚙️ My Settings")
st.markdown("---")

tab1, tab2 = st.tabs(["**👤 My Profile & Preferences**", "**🔑 Change Password**"])

# --- TAB 1: Profile and Preferences ---
with tab1:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Profile Picture")
        if profile.get("profile_picture_url"):
            photo_url = f"{API_BASE_URL}{profile['profile_picture_url']}"
            st.image(photo_url, width=200, caption="Current Photo")
        else:
            st.image("https://via.placeholder.com/200x200.png?text=No+Photo", width=200, caption="No Photo Uploaded")

        uploaded_photo = st.file_uploader("Upload a new photo (max 2MB)", type=["png", "jpg", "jpeg"])
        if uploaded_photo:
            if st.button("Upload Photo", type="primary", use_container_width=True):
                files = {"file": (uploaded_photo.name, uploaded_photo, uploaded_photo.type)}
                with st.spinner("Uploading..."):
                    response = api.post_files("/users/me/photo", files=files)
                if response:
                    st.toast("Photo updated successfully!", icon="📸")
                    fetch_user_profile()
                    st.rerun()

    with col2:
        st.subheader("Personal Information")
        with st.form("profile_form"):
            # Safely parse the date of birth
            dob_value = None
            if profile.get("date_of_birth"):
                try:
                    dob_value = datetime.strptime(profile["date_of_birth"], "%Y-%m-%d").date()
                except (ValueError, TypeError):
                    dob_value = None

            full_name = st.text_input("Full Name", value=profile.get("full_name", ""))
            date_of_birth = st.date_input("Date of Birth", value=dob_value, min_value=datetime(1920, 1, 1).date())
            address = st.text_area("Address", value=profile.get("address", ""))

            if st.form_submit_button("Save Profile Changes", use_container_width=True):
                update_data = {
                    "full_name": full_name.strip(),
                    "date_of_birth": str(date_of_birth) if date_of_birth else None,
                    "address": address.strip()
                }
                with st.spinner("Saving..."):
                    response = api.put("/users/me", json_data=update_data)
                if response:
                    st.toast("Profile updated successfully!", icon="✅")
                    fetch_user_profile()
                    st.rerun()

        st.markdown("---")
        st.subheader("Preferences")

        def handle_reminder_toggle():
            """Callback to update reminder preference instantly."""
            new_status = st.session_state.reminder_toggle
            with st.spinner("Updating preference..."):
                response = api.put("/users/me", json_data={"send_reminders": new_status})
            if response:
                fetch_user_profile()
                st.toast(f"Email reminders turned {'ON' if new_status else 'OFF'}.", icon="📧")
            else:
                # If the API call fails, revert the toggle to its previous state
                st.session_state.reminder_toggle = not new_status

        st.toggle(
            "Receive Daily Medication Reminders by Email",
            value=profile.get("send_reminders", True),
            key="reminder_toggle",
            on_change=handle_reminder_toggle,
            help="If enabled, you will receive an email every morning with your medication schedule."
        )

# --- TAB 2: Change Password ---
with tab2:
    st.subheader("Set a New Password")
    with st.form("password_form", clear_on_submit=True):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_new_password = st.text_input("Confirm New Password", type="password")

        if st.form_submit_button("Update Password", type="primary", use_container_width=True):
            if not all([current_password, new_password, confirm_new_password]):
                st.warning("Please fill in all password fields.")
            elif new_password != confirm_new_password:
                st.error("The new passwords do not match.")
            elif len(new_password) < 8:
                st.error("The new password must be at least 8 characters long.")
            else:
                update_data = {"current_password": current_password, "new_password": new_password}
                with st.spinner("Updating your password..."):
                    response = api.put("/users/me/password", json_data=update_data)
                if response and response.status_code == 200:
                    st.success("Your password has been updated successfully!")
                # Specific error handling is now done within the ApiClient
