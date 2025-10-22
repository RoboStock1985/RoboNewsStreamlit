import time
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from backend_functionality import sbase_functions, auth_utils
# from backend_functionality import theme_utils

st.set_page_config(layout="wide")
st.set_option('client.showErrorDetails', False)

st.set_page_config(page_title="RoboNews", layout="wide")

supabase = sbase_functions.get_authenticated_client()
auth_utils.require_login(supabase)
user_id = st.session_state.user_id
# theme_utils.check_theme(supabase, user_id)

# ---------------------------
# Helper functions
# ---------------------------


def get_user_stocks(user_id):

    """Fetch stocks this user has access to."""

    response = supabase.table("user_stock_selection").select("ticker").eq("user_id", user_id).execute()

    return [row["ticker"] for row in response.data] if response.data else []


def get_financial_news(stock_symbol, limit=10):

    """Fetch latest financial news for the selected stock."""

    response = (
        supabase.table("financial_news")
        .select("company_name, stock_symbol, headline, source, news_item_timestamp, url")
        .eq("stock_symbol", stock_symbol)
        .order("news_item_timestamp", desc=True)
        .limit(limit)
        .execute()
    )
    return response.data if response.data else []


def get_stock_data(stock_symbol, limit=200):

    """Fetch recent stock price data."""

    response = (
        supabase.table("stock_data")
        .select("date, open, high, low, close, volume")
        .eq("ticker", stock_symbol)
        .order("date", desc=True)
        .limit(limit)
        .execute()
    )
    data = response.data or []
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    return df


# ---------------------------
# Streamlit Page
# ---------------------------
st.set_page_config(page_title="Stock Analysis", layout="wide")

st.title("📊 Stock Analysis Dashboard")

# Fetch available stocks
available_stocks = get_user_stocks(user_id)
if not available_stocks:
    st.warning("You do not have access to any stocks yet. Please select some on your Profile page.")
    st.stop()

selected_stock = st.selectbox("Select a stock to analyze:", available_stocks)

# ---------------------------
# NEWS TICKER
# ---------------------------
st.subheader(f"📰 Live Financial News for {selected_stock}")

news_container = st.empty()
REFRESH_INTERVAL = 600  # seconds


def render_news_ticker(news_items):

    """Render smooth horizontal ticker within Streamlit width."""

    if not news_items:
        st.info("No recent news available.")
        return

    ticker_items = ""
    for item in news_items:
        headline = item["headline"]
        source = item["source"]
        url = item["url"]
        ts = item["news_item_timestamp"]
        entry = f"<span style='margin-right: 60px;'>🗞️ <a href='{url}' target='_blank'><b>{headline}</b></a> <small>({source}, {ts})</small></span>"
        ticker_items += entry

    ticker_html = f"""
    <div class="ticker-wrap">
        <div class="ticker">
            {ticker_items * 2}
        </div>
    </div>

    <style>
        .ticker-wrap {{
            width: 100%;
            overflow: hidden;
            background-color: #f9f9f9;
            border-radius: 8px;
            padding: 8px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .ticker {{
            display: inline-block;
            white-space: nowrap;
            animation: ticker-scroll 60s linear infinite;
        }}
        @keyframes ticker-scroll {{
            0% {{ transform: translateX(0%); }}
            100% {{ transform: translateX(-50%); }}
        }}
        a {{
            color: #1f77b4;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
    </style>
    """
    st.markdown(ticker_html, unsafe_allow_html=True)


# ---------------------------
# STOCK CHART
# ---------------------------
def render_stock_chart(df, stock_symbol):

    """Plot candlestick chart with volume."""

    if df.empty:
        st.warning("No stock data available.")
        return

    fig = go.Figure()

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df["date"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="Price",
        increasing_line_color="green",
        decreasing_line_color="red"
    ))

    # Volume as bars
    fig.add_trace(go.Bar(
        x=df["date"],
        y=df["volume"],
        name="Volume",
        marker_opacity=0.3,
        yaxis="y2"
    ))

    # Layout
    fig.update_layout(
        title=f"{stock_symbol} Price & Volume",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        yaxis2=dict(
            overlaying="y",
            side="right",
            showgrid=False,
            title="Volume"
        ),
        height=600,
        template="plotly_white",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)


# ---------------------------
# PAGE LOOP
# ---------------------------
chart_container = st.empty()

with st.empty():
    while True:
        # Refresh news
        news_data = get_financial_news(selected_stock, limit=10)
        news_container.empty()
        with news_container.container():
            render_news_ticker(news_data)

        # Refresh stock data
        df_stock = get_stock_data(selected_stock, limit=200)
        chart_container.empty()
        with chart_container.container():
            render_stock_chart(df_stock, selected_stock)

        time.sleep(REFRESH_INTERVAL)


if "session" in st.session_state and st.session_state.session:
    if st.sidebar.button("🚪 Logout"):

        st.session_state.session = None
        supabase.auth.sign_out()
        st.switch_page("Login Page.py")

st.title("📰 RoboNews")

if "session" in st.session_state and st.session_state.session:
    if st.sidebar.button("🚪 Logout"):

        st.session_state.session = None
        supabase.auth.sign_out()
        st.switch_page("Login Page.py")
