import streamlit as st
from backend_functionality import auth_utils

from backend_functionality import sbase_functions
supabase_client = sbase_functions.get_authenticated_client()

st.set_option('client.showErrorDetails', False)

# 👇 Enforce login before anything else
auth_utils.require_login(supabase_client)

st.title("Profile Page")

st.write("Summary Of Profile. Details. Options etc.")

st.write("Add in capability of user to select which stocks they want to follow. These will be tiered by Plan-level and only changable once a month.")

if "session" in st.session_state and st.session_state.session:
    if st.sidebar.button("🚪 Logout"):

        st.session_state.session = None
        supabase_client.auth.sign_out()
        st.switch_page("Login Page.py")