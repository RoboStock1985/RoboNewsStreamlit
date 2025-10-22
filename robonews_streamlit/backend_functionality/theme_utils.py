import streamlit as st


def check_theme(supabase, user_id):

    # get user theme from supabase
    try:
        user_profile = supabase.table("users").select("theme").eq("user_id", user_id).execute()
        theme = user_profile.data[0]["theme"] if user_profile.data else "light"
    except Exception:
        theme = "light"

    st.session_state.theme = theme

    # Immediately after page config:
    if st.session_state.theme == "dark":
        st.markdown("""<style>
    /* Background and text */
    [data-testid="stAppViewContainer"] {
        background-color: #0E1117 !important;
        color: #FAFAFA !important;
    }

    [data-testid="stHeader"] {
        background-color: #0E1117 !important;
        color: #FAFAFA !important;
    }

    [data-testid="stSidebar"] {
        background-color: #131722 !important;
        color: #FAFAFA !important;
    }

    /* Inputs and selects */
    input, .stTextInput>div>div>input, .stNumberInput>div>input, select {
        background-color: #1E1E1E !important;
        color: white !important;
    }

    /* Buttons */
    .stButton>button {
        background-color: #1f77b4 !important;
        color: white !important;
    }

    /* Images slightly darker */
    .stImage img {
        filter: brightness(0.9);
    }
    </style>
    """, unsafe_allow_html=True)