import streamlit as st

from backend_functionality import sbase_functions
supabase_client = sbase_functions.get_authenticated_client()


def login(email, password):

    try:
        res = supabase_client.auth.sign_in_with_password({"email": email, "password": password})
        session = res.session

        # Store user + tokens in session_state
        st.session_state.user = res.user
        st.session_state.access_token = session.access_token
        st.session_state.refresh_token = session.refresh_token

        st.success(f"Welcome back, {email}!")

        # re-direct to another page - Profile? RoboNews?

    except Exception as e:
        st.error(f"Login failed: {e}")


def signup(email, password):

    try:
        res = supabase_client.auth.sign_up({"email": email, "password": password})
        st.success("Check your inbox for a confirmation email.")

        # TODO - add in checking of existing user and re-direct to reset password via email

    except Exception as e:
        st.error(f"Sign up failed: {e}")


def send_password_reset(email):

    try:
        res = supabase_client.auth.reset_password_email(email)
        st.success(f"📬 Password reset email sent to {email}")
    except Exception as e:
        st.error(f"Failed to send reset email: {e}")


def logout():

    supabase_client.auth.sign_out()

    for key in ["user", "access_token", "refresh_token"]:
        if key in st.session_state:
            del st.session_state[key]

    st.success("Logged out.")
