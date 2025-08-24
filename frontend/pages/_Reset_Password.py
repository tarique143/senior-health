# /frontend/pages/_Reset_Password.py
# The underscore prefix hides this page from the default Streamlit sidebar navigation.

import os

import requests
import streamlit as st

# --- 1. PAGE CONFIGURATION ---
# Use a centered layout and collapse the sidebar for a focused experience.
st.set_page_config(page_title="Reset Password", layout="centered", initial_sidebar_state="collapsed")

# --- 2. API SETUP ---
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

class ApiClient:
    """A minimal API client for this page's specific needs."""
    def __init__(self, base_url: str):
        self.base_url = base_url

    def post(self, endpoint: str, json_data: dict):
        """Makes a POST request and handles potential errors."""
        try:
            response = requests.post(f"{self.base_url}{endpoint}", json=json_data, timeout=15)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            # Provide a user-friendly error from the API response.
            error_detail = e.response.json().get('detail', 'An unknown error occurred.')
            st.error(f"Failed to reset password: {error_detail}")
        except requests.exceptions.RequestException:
            st.error("Connection Error: Could not connect to the server.")
        return None

api = ApiClient(API_BASE_URL)

# --- 3. CUSTOM STYLING ---
# Hide the (already collapsed) sidebar and center the form vertically.
st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            display: none;
        }
        .main .st-emotion-cache-1y4p8pa {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 90vh;
        }
    </style>
""", unsafe_allow_html=True)


# --- 4. PAGE LOGIC ---
st.title("🔑 Set Your New Password")

# Retrieve the reset token from the URL's query parameters.
# e.g., http://.../Reset_Password?token=YOUR_TOKEN_HERE
query_params = st.query_params
token = query_params.get("token")

if not token:
    st.error("The password reset link is invalid or missing a token.")
    st.info("Please request a new password reset link from the login page.")
    st.page_link("streamlit_app.py", label="Back to Login", icon="👈")
else:
    st.write("Please enter and confirm your new password below.")
    with st.form("reset_password_form"):
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        submitted = st.form_submit_button("Reset Password", use_container_width=True, type="primary")

        if submitted:
            if not new_password or not confirm_password:
                st.warning("Please fill in both password fields.")
            elif new_password != confirm_password:
                st.error("The two passwords do not match. Please try again.")
            elif len(new_password) < 8:
                st.error("Your new password must be at least 8 characters long.")
            else:
                with st.spinner("Updating your password..."):
                    response = api.post(
                        "/users/reset-password",
                        json_data={"token": token, "new_password": new_password}
                    )

                if response and response.status_code == 200:
                    # Set a flag in session_state to show a success message on the login page.
                    st.session_state['password_reset_success'] = True
                    # Redirect the user back to the login page.
                    st.switch_page("streamlit_app.py")
