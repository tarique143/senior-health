# /frontend/pages/Settings.py (Final Version)

import streamlit as st
import requests
import os
from datetime import datetime

# Hamari nayi UI file se functions import karein
from ui_components import apply_styles, build_sidebar

# Page ki shuruaat mein styles aur double-sidebar fix apply karein
apply_styles()

# --- CONFIGURATION & API CLIENT ---
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

class ApiClient:
    def __init__(self, base_url): self.base_url = base_url
    def _get_headers(self):
        token = st.session_state.get("access_token")
        if not token: st.warning("Please login first."); st.switch_page("streamlit_app.py"); st.stop()
        return {"Authorization": f"Bearer {token}"}
    def _make_request(self, method, endpoint, **kwargs):
        try: return requests.request(method, f"{self.base_url}{endpoint}", headers=self._get_headers(), timeout=20, **kwargs)
        except requests.exceptions.RequestException: st.error("Connection Error."); return None
    def get(self, endpoint): return self._make_request("GET", endpoint)
    def put(self, endpoint, json=None): return self._make_request("PUT", endpoint, json=json)
    def post_files(self, endpoint, files=None):
        try:
            headers = {"Authorization": self._get_headers()["Authorization"]}
            return requests.post(f"{self.base_url}{endpoint}", headers=headers, files=files, timeout=20)
        except requests.exceptions.RequestException: st.error("Connection Error."); return None

api = ApiClient(API_BASE_URL)

# --- SECURITY CHECK ---
if 'access_token' not in st.session_state:
    st.warning("Please login first to access this page.")
    st.switch_page("streamlit_app.py")
    st.stop()

# --- PAGE SETUP ---
st.set_page_config(page_title="Settings", layout="wide")
build_sidebar() # Hamara custom sidebar banayein

# --- HELPER FUNCTIONS ---
def fetch_user_profile():
    response = api.get("/users/me")
    if response and response.status_code == 200:
        st.session_state.user_profile = response.json()
    else:
        st.error("Could not load your profile. Please try logging in again."); st.stop()

# --- INITIAL DATA FETCH ---
if 'user_profile' not in st.session_state:
    with st.spinner("Loading your profile..."): fetch_user_profile()

profile = st.session_state.user_profile

# --- PAGE CONTENT ---
st.header("⚙️ My Settings")
st.markdown("---")

tab1, tab2 = st.tabs(["**👤 My Profile & Preferences**", "**🔑 Change Password**"])

with tab1:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Profile Picture")
        if profile.get("profile_picture_url"):
            photo_url = f"{API_BASE_URL}{profile['profile_picture_url']}"
            st.image(photo_url, width=200, caption="Current Photo")
        else:
            st.image("https://via.placeholder.com/200x200.png?text=No+Photo", width=200, caption="No Photo Uploaded")
        
        uploaded_photo = st.file_uploader("Upload a new photo", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
        if uploaded_photo:
            if st.button("Upload Photo", type="primary"):
                files = {"file": (uploaded_photo.name, uploaded_photo, uploaded_photo.type)}
                with st.spinner("Uploading..."): response = api.post_files("/users/me/photo", files=files)
                if response and response.status_code == 200:
                    st.toast("Photo updated!", icon="📸"); fetch_user_profile(); st.rerun()
                else: st.error("Upload failed. Please try a smaller image.")
    with col2:
        st.subheader("Personal Information")
        with st.form("profile_form", border=False):
            dob_value = None
            if profile.get("date_of_birth"):
                try: dob_value = datetime.strptime(profile["date_of_birth"], "%Y-%m-%d").date()
                except (ValueError, TypeError): dob_value = None
            full_name = st.text_input("Full Name", value=profile.get("full_name", ""))
            date_of_birth = st.date_input("Date of Birth", value=dob_value)
            address = st.text_area("Address", value=profile.get("address", ""))
            if st.form_submit_button("Save Profile Changes", use_container_width=True):
                update_data = {"full_name": full_name, "date_of_birth": str(date_of_birth) if date_of_birth else None, "address": address}
                with st.spinner("Saving..."): response = api.put("/users/me", json=update_data)
                if response and response.status_code == 200:
                    st.toast("Profile updated!", icon="✅"); fetch_user_profile(); st.rerun()
                else: st.error("Failed to update profile.")
        
        st.markdown("---")
        st.subheader("Preferences")
        current_reminder_status = profile.get("send_reminders", True)
        def handle_toggle_change():
            new_status = st.session_state.reminder_toggle
            with st.spinner("Updating..."): response = api.put("/users/me", json={"send_reminders": new_status})
            if response and response.status_code == 200:
                fetch_user_profile(); st.toast(f"Email reminders turned {'ON' if new_status else 'OFF'}", icon="📧")
            else:
                st.error("Failed to update preference."); st.session_state.reminder_toggle = not new_status
        
        st.toggle("Receive Daily Medication Reminders by Email", value=current_reminder_status, key="reminder_toggle",
                  on_change=handle_toggle_change, help="If on, you will receive an email every morning with your schedule.")

with tab2:
    st.subheader("Set a New Password")
    with st.form("password_form", border=False, clear_on_submit=True):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_new_password = st.text_input("Confirm New Password", type="password")
        if st.form_submit_button("Update Password", type="primary", use_container_width=True):
            if not all([current_password, new_password, confirm_new_password]): st.warning("Please fill all password fields.")
            elif new_password != confirm_new_password: st.error("New passwords do not match.")
            else:
                update_data = {"current_password": current_password, "new_password": new_password}
                with st.spinner("Updating..."): response = api.put("/users/me/password", json=update_data)
                if response and response.status_code == 200: st.success("Password updated successfully!")
                else:
                    error_detail = "Failed to update password. Incorrect current password?"
                    if response and response.json(): error_detail = response.json().get('detail', error_detail)
                    st.error(error_detail)
