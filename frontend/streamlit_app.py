# frontend/streamlit_app.py (Updated for Password Reset)

import streamlit as st
import requests
import time
import os

# --- CONFIGURATION & PAGE CONFIG ---
st.set_page_config(page_title="Health Companion", layout="wide", initial_sidebar_state="collapsed")

# --- BACKEND API URL ---
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
 
# --- API CLIENT CLASS ---
class ApiClient:
    def __init__(self, base_url): self.base_url = base_url
    def _get_headers(self):
        token = st.session_state.get("token", None)
        if token: return {"Authorization": f"Bearer {token}"}
        return {}
    def _make_request(self, method, endpoint, **kwargs):
        try:
            return requests.request(method, f"{self.base_url}{endpoint}", headers=self._get_headers(), timeout=10, **kwargs)
        except requests.exceptions.RequestException:
            st.error("Connection Error: Could not connect to the backend server."); return None
    def get(self, endpoint, params=None): return self._make_request("GET", endpoint, params=params)
    def post(self, endpoint, data=None, json=None): return self._make_request("POST", endpoint, data=data, json=json)

api = ApiClient(API_BASE_URL)

# --- STYLING (Same as before) ---
def apply_global_styles():
    st.markdown("""<style>...</style>""", unsafe_allow_html=True) # Assuming styles are here

def apply_themed_styles():
    # Assuming themed styles logic is here
    pass

# --- HEADER (Same as before) ---
def create_header():
    # Assuming header logic is here
    pass

# --- AUTHENTICATION PAGE FUNCTION ---
def show_login_register_page():
    st.markdown("""
        <style>
            section[data-testid="stSidebar"] { display: none; }
            .st-emotion-cache-1y4p8pa {
                display: flex; flex-direction: column;
                justify-content: center; align-items: center;
                height: 100vh;
            }
        </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        _, c2, _ = st.columns([1, 1.5, 1])
        with c2:
            st.markdown('<div class="login-container" style="box-shadow: 0 8px 16px rgba(0,0,0,0.1); padding: 2rem 3rem; border-radius: 15px;">', unsafe_allow_html=True)
            st.markdown(
                """<div style="text-align: center;"><h1 style="color: #0055a3; font-weight: 700;">🩺 Welcome!</h1><p style="color: #555; font-size: 1.2rem;">Your Health Companion</p></div>""",
                unsafe_allow_html=True
            )
            st.write("")
            if st.session_state.get('just_registered', False):
                st.success("Registration successful! Please sign in."); del st.session_state['just_registered']

            # Check if password was just reset
            if st.session_state.get('password_reset_success', False):
                st.success("Password reset successfully! Please sign in with your new password.")
                del st.session_state['password_reset_success']


            login_tab, register_tab = st.tabs(["**Sign In**", "**Create Account**"])
            with login_tab:
                with st.form("login_form"):
                    email = st.text_input("Email", placeholder="you@example.com")
                    password = st.text_input("Password", type="password")
                    if st.form_submit_button("Sign In", use_container_width=True):
                        with st.spinner("Authenticating..."):
                            response = api.post("/users/token", data={"username": email, "password": password})
                        if response and response.status_code == 200:
                            st.session_state["token"] = response.json()["access_token"]; st.session_state["user_email"] = email
                            st.toast("Login Successful!", icon="🎉"); st.rerun()
                        else: st.error("Login Failed: Incorrect email or password.")
            
            with register_tab:
                with st.form("register_form"):
                    full_name = st.text_input("Full Name")
                    new_email = st.text_input("Email", placeholder="you@example.com")
                    new_password = st.text_input("Create Password", type="password")
                    if st.form_submit_button("Create Account", use_container_width=True):
                        with st.spinner("Registering..."):
                            response = api.post("/users/register", json={"full_name": full_name, "email": new_email, "password": new_password})
                        if response and response.status_code == 201:
                            st.session_state['just_registered'] = True; st.rerun()
                        else:
                            error_detail = response.json().get('detail', 'Email may already be registered.') if response else "Could not connect to server."
                            st.error(f"Registration Failed: {error_detail}")
            
            st.write("---")
            if st.session_state.get("show_forgot_password", False):
                st.subheader("Reset Your Password")
                with st.form("reset_form"):
                    email_reset = st.text_input("Enter your Email Address", key="reset_email")
                    c1_reset, c2_reset = st.columns(2)
                    with c1_reset:
                        if st.form_submit_button("Send Reset Link", use_container_width=True, type="primary"):
                            ### <<< BADLAV YAHAN HUA HAI
                            with st.spinner("Sending..."):
                                response = api.post("/users/forgot-password", json={"email": email_reset})
                            
                            # Hum hamesha success message dikhayenge taaki koi guess na kar paaye ki email exist karta hai ya nahi.
                            st.success("If an account with this email exists, a reset link has been sent.")
                            st.session_state.show_forgot_password = False
                            st.rerun()
                            ### <<< BADLAV YAHAN KHATAM HUA

                    with c2_reset:
                        if st.form_submit_button("Cancel", use_container_width=True):
                            st.session_state.show_forgot_password = False; st.rerun()
            else:
                 if st.button("Forgot Password?", type="secondary", use_container_width=True):
                    st.session_state.show_forgot_password = True; st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

# --- MAIN APPLICATION CONTROLLER (Same as before) ---
def main():
    # Assuming main logic is here
    if "token" not in st.session_state:
        show_login_register_page()
    else:
        # Show main app
        st.title("Main App Area")
        st.write("Welcome!")


if __name__ == "__main__":
    main()
