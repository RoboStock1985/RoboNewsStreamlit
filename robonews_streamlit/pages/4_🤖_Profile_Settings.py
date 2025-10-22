import streamlit as st
import os
import uuid
from backend_functionality import sbase_functions, auth_utils
# from backend_functionality import theme_utils

# ---------------------------
# Page config
# ---------------------------
st.set_page_config(page_title="Profile Settings", layout="centered")

# ---------------------------
# Supabase client & login
# ---------------------------
supabase = sbase_functions.get_authenticated_client()
auth_utils.require_login(supabase)
user_id = st.session_state.user_id
# theme_utils.check_theme(supabase, user_id)


# ---------------------------
# Load user profile
# ---------------------------
def get_user_profile(user_id):

    response = supabase.table("users").select("*").eq("user_id", user_id).execute()
    if response.data:
        return response.data[0]
    return {
        "user_id": user_id,
        "display_name": "",
        "avatar_url": "",
        "max_stock_selection": 5,
        "theme": "light"
    }


profile = get_user_profile(user_id)

# ---------------------------
# Theme selector
# ---------------------------
# theme_choice = st.radio(
#     "Select Theme",
#     options=["light", "dark"],
#     index=0 if st.session_state.theme == "light" else 1
# )

# if theme_choice != st.session_state.theme:
#     st.session_state.theme = theme_choice

#     # st.session_state.theme_applied = False  # force re-injection
#     # st.rerun()

# ---------------------------
# Page title
# ---------------------------
st.title("👤 Profile Settings")

# ---------------------------
# Profile layout
# ---------------------------
col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("**Current Avatar:**")
    if profile.get("avatar_url"):
        st.image(profile["avatar_url"], width=150)
    else:
        st.image("https://nlmvrvasxoljtudzofhv.supabase.co/storage/v1/object/public/avatars/300px-Marvin_the_Paranoid_Android.webp.png", width=150)

    uploaded_file = st.file_uploader("Upload New Avatar", type=["png", "jpg", "jpeg"])

with col2:
    display_name = st.text_input("Display Name", value=profile.get("display_name", ""))
    max_selection = st.number_input(
        "Maximum Number of Stock Selections",
        min_value=1,
        max_value=20,
        value=profile.get("max_stock_selection", 5),
        step=1
    )

st.markdown("---")


# ---------------------------
# Avatar upload helper
# ---------------------------
def upload_avatar(user_id, uploaded_file):

    if uploaded_file is None:
        return None

    file_ext = os.path.splitext(uploaded_file.name)[1]
    unique_filename = f"{user_id}_{uuid.uuid4()}{file_ext}"
    file_path = f"avatars/{unique_filename}"
    file_bytes = uploaded_file.getvalue()

    try:
        response = supabase.storage.from_("avatars").upload(
            path=file_path,
            file=file_bytes,
            file_options={"content-type": uploaded_file.type}
        )
        if hasattr(response, "error") and response.error is not None:
            st.error(f"Upload failed: {response.error.message}")
            return None

        public_url = supabase.storage.from_("avatars").get_public_url(file_path)
        return public_url

    except Exception as e:
        st.error(f"Avatar upload failed: {e}")
        return None


# ---------------------------
# Save profile
# ---------------------------
def update_user_profile(user_id, display_name, avatar_url, max_selection, theme='light'):

    # delete the previous record if exists
    supabase.table("users").delete().eq("user_id", user_id).execute()

    supabase.table("users").upsert({
        "user_id": user_id,
        "display_name": display_name,
        "avatar_url": avatar_url,
        "max_stock_selection": max_selection,
        "theme": theme
    }).execute()


if st.button("💾 Save Profile Settings"):
    avatar_url = profile.get("avatar_url")
    if uploaded_file is not None:
        with st.spinner("Uploading avatar..."):
            avatar_url = upload_avatar(user_id, uploaded_file)

    with st.spinner("Saving changes..."):

        # TODO - remove this when using themes
        st.session_state.theme = "light"
        update_user_profile(user_id, display_name, avatar_url, max_selection, st.session_state.theme)

    st.success("✅ Profile updated successfully!")
    st.session_state.avatar_url = avatar_url
    st.session_state.display_name = display_name

    st.rerun()  # re-render page with updated info and theme

# ---------------------------
# Display current settings
# ---------------------------
st.markdown("### Current Settings")
st.write(f"**Display Name:** {display_name}")
st.write(f"**Max Stock Selections:** {max_selection}")
# st.write(f"**Theme:** {st.session_state.theme.capitalize()}")
if profile.get("avatar_url"):
    st.image(profile["avatar_url"], width=100)

# ---------------------------
# Optional Logout (sidebar)
# ---------------------------
if "session" in st.session_state and st.session_state.session:
    if st.sidebar.button("🚪 Logout"):
        st.session_state.session = None
        supabase.auth.sign_out()
        st.switch_page("Login Page.py")
