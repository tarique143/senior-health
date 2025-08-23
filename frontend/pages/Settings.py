# frontend/pages/Settings.py (Fully Updated for Photo Upload)

import streamlit as st
import requests
import os
from datetime import datetime

# --- CONFIGURATION & API CLIENT ---
st.set_page_config(page_title="Settings", layout="wide")
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

class ApiClient:
    # ... (Same ApiClient class as before) ...
    # === API CLIENT MEIN NAYA METHOD ADD KAREIN ===
    def post_files(self, endpoint, files=None):
        return self._make_request("POST", endpoint, files=files)
    # (Pichli file se same ApiClient class yahan copy karein, aur upar wala method add karein)
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
            # We remove headers for file uploads, requests will set the correct Content-Type
            headers = self._get_headers() if 'files' not in kwargs else {"Authorization": self._get_headers()["Authorization"]}
            return requests.request(method, f"{self.base_url}{endpoint}", headers=headers, timeout=20, **kwargs)
        except requests.exceptions.RequestException:
            st.error("Connection Error: Could not connect to the backend server."); return None
    def get(self, endpoint): return self._make_request("GET", endpoint)
    def put(self, endpoint, json=None): return self._make_request("PUT", endpoint, json=json)


api = ApiClient(API_BASE_URL)

# ... (Security check) ...
if 'token' not in st.session_state:
    st.warning("Please login first to access this page.")
    st.switch_page("streamlit_app.py")
    st.stop()


# ... (Fetch user data logic) ...
if 'user_profile' not in st.session_state:
    with st.spinner("Loading your profile..."):
        response = api.get("/users/me")
        if response and response.status_code == 200:
            st.session_state.user_profile = response.json()
        else:
            st.error("Could not load your profile. Please try logging in again."); st.stop()

profile = st.session_state.user_profile

# --- PAGE CONTENT ---
st.header("⚙️ My Settings")
st.markdown("---")

# TABS for different settings
tab1, tab2 = st.tabs(["**👤 My Profile**", "**🔑 Change Password**"])

with tab1:
    # Profile Picture and Uploader on the side
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Profile Picture")
        
        # ### <<< NAYA CODE: PHOTO DIKHANE KE LIYE
        if profile.get("profile_picture_url"):
            # Construct the full URL
            photo_url = f"{API_BASE_URL}/static{profile['profile_picture_url']}"
            st.image(photo_url, width=200)
        else:
            st.image("https://via.placeholder.com/200x200.png?text=No+Photo", width=200)
        
        # ### <<< NAYA CODE: PHOTO UPLOAD KARNE KE LIYE
        uploaded_photo = st.file_uploader(
            "Upload a new photo",
            type=["png", "jpg", "jpeg"],
            label_visibility="collapsed"
        )
        if uploaded_photo is not None:
            if st.button("Upload Photo", type="primary"):
                files = {"file": (uploaded_photo.name, uploaded_photo, uploaded_photo.type)}
                with st.spinner("Uploading..."):
                    response = api.post_files("/users/me/photo", files=files)
                
                if response and response.status_code == 200:
                    st.toast("Photo updated!", icon="📸")
                    st.session_state.user_profile = response.json() # Refresh profile data
                    st.rerun()
                else:
                    st.error("Upload failed. Please try a smaller image.")

    with col2:
        st.subheader("Update Personal Information")
        with st.form("profile_form", border=False):
            # ... (Form fields for name, dob, address - Same as before) ...
            dob_value = None
            if profile.get("date_of_birth"):
                try: dob_value = datetime.strptime(profile["date_of_birth"], "%Y-%m-%d").date()
                except (ValueError, TypeError): dob_value = None
            full_name = st.text_input("Full Name", value=profile.get("full_name", ""))
            date_of_birth = st.date_input("Date of Birth", value=dob_value)
            address = st.text_area("Address", value=profile.get("address", ""))
            
            if st.form_submit_button("Save Profile Changes", use_container_width=True):
                # ... (Form submission logic - Same as before) ...
                update_data = {"full_name": full_name, "date_of_birth": str(date_of_birth) if date_of_birth else None, "address": address}
                with st.spinner("Saving..."):
                    response = api.put("/users/me", json=update_data)
                if response and response.status_code == 200:
                    st.toast("Profile updated successfully!", icon="✅")
                    st.session_state.user_profile = response.json()
                    st.rerun()
                else:
                    st.error("Failed to update profile.")


with tab2:
    # ... (Change Password form - Same as before) ...
    st.subheader("Set a New Password")
    with st.form("password_form", border=False):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_new_password = st.text_input("Confirm New Password", type="password")
        if st.form_submit_button("Update Password", type="primary", use_container_width=True):
            if not all([current_password, new_password, confirm_new_password]): st.warning("Please fill all password fields.")
            elif new_password != confirm_new_password: st.error("New passwords do not match.")
            else:
                update_data = {"current_password": current_password, "new_password": new_password}
                with st.spinner("Updating..."):
                    response = api.put("/users/me/password", json=update_data)
                if response and response.status_code == 200: st.success("Password updated successfully!")
                else:
                    error_detail = "Failed to update password. Incorrect current password?"
                    if response:
                        try: error_detail = response.json().get('detail', error_detail)
                        except: pass
                    st.error(error_detail)


st.markdown("---")
# ... (Logout button - Same as before) ...
if st.button("Logout", use_container_width=True):
    # Clear session state and go to login page
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.toast("Logged out successfully.")
    st.switch_page("streamlit_app.py")
