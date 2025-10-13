
import os
import streamlit as st
from supabase import create_client

from dotenv import load_dotenv

st.set_option('client.showErrorDetails', False)

# -------------------------
# 🧰 Supabase config
# -------------------------

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------
# 💾 Keep user logged in (session state)
# -------------------------

if "session" not in st.session_state:
    st.session_state.session = None

params = st.query_params

# -------------------------
# 🧍 User already logged in?
# -------------------------
if st.session_state.session:

    st.write("👋 Welcome! You are logged in.")
    if st.button("Logout"):
        st.session_state.session = None
        supabase_client.auth.sign_out()
        st.rerun()

else:
    # -------------------------
    # 🔐 Login and Signup Forms
    # -------------------------
    tabs = st.tabs(["🔑 Login", "📝 Sign Up", "🔁 Reset Password"])

    with tabs[0]:
        st.subheader("Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            try:
                res = supabase_client.auth.sign_in_with_password({"email": email, "password": password})
                if res.user:
                    st.session_state.session = {
                        "access_token": res.session.access_token,
                        "refresh_token": res.session.refresh_token
                    }
                    st.success(f"Welcome {email}!")
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
            except Exception as e:
                st.error(f"Login failed: {e}")

    with tabs[1]:
        st.subheader("Sign Up")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        if st.button("Sign Up"):
            try:
                res = supabase_client.auth.sign_up({"email": email, "password": password})
                if res.user:
                    st.success("✅ Check your email to confirm your account.")
                else:
                    st.error("Sign up failed.")
            except Exception as e:
                st.error(f"Error: {e}")

    with tabs[2]:
        st.subheader("Reset Password")
        email = st.text_input("Enter your email to reset password", key="reset_email")
        if st.button("Send Reset Email"):
            try:
                supabase_client.auth.reset_password_for_email(
                    email,
                    options={"redirect_to": "http://localhost:8501"}  # or your deployed URL
                )
                st.success("📩 Password reset email sent. Check your inbox.")
            except Exception as e:
                st.error(f"Error: {e}")

if "session" in st.session_state and st.session_state.session:
    if st.sidebar.button("🚪 Logout"):

        st.session_state.session = None
        supabase_client.auth.sign_out()
        st.switch_page("Login Page.py")
