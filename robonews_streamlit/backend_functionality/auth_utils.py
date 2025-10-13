# auth_utils.py
import time
import streamlit as st


def require_login(supabase_client):

    """Redirects user to login page if no session is stored."""

    if "session" not in st.session_state or not st.session_state.session:
        st.warning("⚠️ You must be logged in to view this page. re-directing to login page...")
        time.sleep(2)
        st.switch_page("Login Page.py")  # 👈 Streamlit's page navigation
    else:
        # Optional: check if session is still valid
        user = supabase_client.auth.get_user(st.session_state.session["access_token"])
        if not user or not user.user:
            st.session_state.session = None
            st.warning("Session expired. Please log in again.")
            st.switch_page("Login Page.py")


def check_login(supabase_client):

    """"""

    if "session" not in st.session_state:
        st.session_state.session = None

    params = st.query_params

    if "access_token" in params and "refresh_token" in params:

        access_token = params["access_token"]
        refresh_token = params["refresh_token"]

        try:
            supabase_client.auth.set_session(access_token, refresh_token)
            st.session_state.session = {
                "access_token": access_token,
                "refresh_token": refresh_token
            }
        except:
            return False

    return True
