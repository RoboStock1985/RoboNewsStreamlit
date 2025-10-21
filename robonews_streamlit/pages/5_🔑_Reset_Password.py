import streamlit as st
from backend_functionality import sbase_functions
from streamlit_url_fragments import get_fragments

st.set_page_config(layout="centered")
st.set_option('client.showErrorDetails', False)

supabase_client = sbase_functions.get_authenticated_client()

current_value = get_fragments()

# # If already logged in then don't need to check this - as they are allowed to change password any time
# if "session" not in st.session_state or not st.session_state.session:

access_token = None
refresh_token = None
token_type = None

if current_value:
    try:
        access_token = current_value["access_token"]
        refresh_token = current_value["refresh_token"]
        token_type = current_value["type"]

        supabase_client.auth.set_session(access_token, refresh_token)
        st.session_state.session = {"access_token": access_token, "refresh_token": refresh_token}

        # -------------------------
        # 👤 Verify user is valid
        # -------------------------
        user_data = supabase_client.auth.get_user(access_token)
        if not user_data or not user_data.user:
            st.error("❌ Invalid or expired recovery token.")
            st.stop()

    except KeyError:
        st.error("❌ No valid recovery token found in the URL.")
        st.stop()

if not access_token or not refresh_token or token_type != "recovery":
    st.error("❌ No valid recovery token found in the URL.")
    st.stop()

# -------------------------
# 🔑 Password reset form
# -------------------------
st.title("🔐 Reset Your Password")
st.write(f"Resetting password for: **{user_data.user.email}**")

new_password = st.text_input("New Password", type="password")
confirm_password = st.text_input("Confirm New Password", type="password")

if st.button("Change Password"):
    if new_password != confirm_password:
        st.error("❌ Passwords do not match.")
    elif len(new_password) < 8:
        st.warning("⚠️ Password should be at least 8 characters.")
    else:
        try:
            supabase_client.auth.update_user({"password": new_password})
            st.success("✅ Password successfully updated!")

            # ✅ Keep the user logged in
            st.session_state.session = {"access_token": access_token, "refresh_token": refresh_token}

            st.info("You are now logged in. You can continue to your dashboard.")
            if st.button("Go to Dashboard"):
                st.switch_page("pages/Profile.py")

        except Exception as e:
            st.error(f"❌ Error updating password: {e}")
