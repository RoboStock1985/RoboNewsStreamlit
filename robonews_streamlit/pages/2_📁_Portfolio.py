import streamlit as st
from backend_functionality import sbase_functions, auth_utils
# from backend_functionality import theme_utils

st.set_page_config(layout="wide")
st.set_option('client.showErrorDetails', False)

supabase = sbase_functions.get_authenticated_client()
auth_utils.require_login(supabase)
user_id = st.session_state.user_id
# theme_utils.check_theme(supabase, user_id)

MAX_SELECTION = 5
STOCKS_TABLE = "logos"
USER_SELECTION_TABLE = "user_stock_selection"
LOGO_MAX_HEIGHT = 150  # max logo height in pixels

# ---------------------------
# Fetch stocks from Supabase
# ---------------------------
@st.cache_data
def get_stocks():

    response = supabase.table(STOCKS_TABLE).select("*").execute()

    return response.data if response.data else []


stocks = get_stocks()

# ---------------------------
# Simulated user ID
# ---------------------------
if "user_id" not in st.session_state:
    st.session_state.user_id = "user_123"


user_id = st.session_state.user_id


# ---------------------------
# Load existing selection
# ---------------------------
@st.cache_data
def get_user_selection(user_id):

    response = supabase.table(USER_SELECTION_TABLE).select("ticker").eq("user_id", user_id).execute()
    return [row["ticker"] for row in response.data] if response.data else []


if "selected_stocks" not in st.session_state:
    st.session_state.selected_stocks = get_user_selection(user_id)

# ---------------------------
# Streamlit UI
# ---------------------------
st.title("📈 Your Stock Profile")
st.write(f"Select up to {MAX_SELECTION} stocks:")

filter_text = st.text_input("🔍 Filter stocks by ticker:")
filtered_stocks = [s for s in stocks if filter_text.upper() in s["ticker"].upper()] if filter_text else stocks


def update_selection(ticker, checked):

    if checked:
        if ticker not in st.session_state.selected_stocks and len(st.session_state.selected_stocks) < MAX_SELECTION:
            st.session_state.selected_stocks.append(ticker)
    else:
        if ticker in st.session_state.selected_stocks:
            st.session_state.selected_stocks.remove(ticker)

# ---------------------------
# Display stocks in a grid
# ---------------------------
cols_per_row = 10
for i in range(0, len(filtered_stocks), cols_per_row):
    cols = st.columns(cols_per_row, gap="small")  # smaller gap between columns
    for j, stock in enumerate(filtered_stocks[i:i+cols_per_row]):
        ticker = stock["ticker"]
        with cols[j]:
            # Logo with max height
            st.image(stock["url"], use_column_width=False, output_format="PNG", clamp=True, width=None)
            # Checkbox
            disabled = len(st.session_state.selected_stocks) >= MAX_SELECTION and ticker not in st.session_state.selected_stocks
            checked = st.checkbox(
                ticker,
                key=f"cb_{ticker}",
                value=ticker in st.session_state.selected_stocks,
                disabled=disabled
            )
            update_selection(ticker, checked)

# ---------------------------
# Sidebar: Dynamic selection display
# ---------------------------
st.sidebar.title("🗂️ Selected Stocks")
if st.session_state.selected_stocks:
    for ticker in st.session_state.selected_stocks:
        stock = next((s for s in stocks if s["ticker"] == ticker), None)
        if stock:
            st.sidebar.image(stock["url"], use_column_width=False)
            st.sidebar.write(stock["ticker"])
else:
    st.sidebar.write("No stocks selected yet.")

st.write("✅ Selected stocks:", st.session_state.selected_stocks)

if st.button("💾 Save Selection"):
    # Delete old selections
    supabase.table(USER_SELECTION_TABLE).delete().eq("user_id", user_id).execute()

    # Insert new selections
    rows = [{"user_id": user_id, "ticker": t} for t in st.session_state.selected_stocks]
    if rows:
        supabase.table(USER_SELECTION_TABLE).insert(rows).execute()

    st.success("✅ Your selection has been saved!")


if "session" in st.session_state and st.session_state.session:
    if st.sidebar.button("🚪 Logout"):

        st.session_state.session = None
        supabase.auth.sign_out()
        st.switch_page("Login Page.py")
