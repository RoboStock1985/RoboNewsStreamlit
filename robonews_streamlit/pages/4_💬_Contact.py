import streamlit as st

from backend_functionality import sbase_functions
from backend_functionality import auth_utils

st.set_option('client.showErrorDetails', False)

supabase_client = sbase_functions.get_authenticated_client()

# 👇 Enforce login before anything else
auth_utils.require_login(supabase_client)

st.title("Contact Us")

st.write("Feel free to reach out to us via the form below!")

st.text_input("Your Name")
st.text_area("Your Message")

if st.button("Submit"):
    st.success("Thank you for reaching out!")

if "session" in st.session_state and st.session_state.session:
    if st.sidebar.button("🚪 Logout"):

        st.session_state.session = None
        supabase_client.auth.sign_out()
        st.switch_page("Login Page.py")
