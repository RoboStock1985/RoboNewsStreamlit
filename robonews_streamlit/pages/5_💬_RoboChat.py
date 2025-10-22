import streamlit as st
from backend_functionality import sbase_functions, auth_utils
# from backend_functionality import theme_utils
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

import html
import emoji

# ---------------------------
# Page config
# ---------------------------
st.set_page_config(page_title="Stock Chat", layout="wide")
supabase = sbase_functions.get_authenticated_client()
auth_utils.require_login(supabase)
user_id = st.session_state.user_id

# ---------------------------
# Apply user theme globally
# ---------------------------
# theme_utils.apply_user_theme(supabase, user_id)

# ---------------------------
# Fetch user stock subscriptions
# ---------------------------
stocks_resp = supabase.table("user_stock_selection").select("ticker").eq("user_id", user_id).execute()
user_stocks = [row["ticker"] for row in stocks_resp.data] if stocks_resp.data else []

if not user_stocks:
    st.warning("You have no subscribed stocks to chat about.")
    st.stop()

# ---------------------------
# Select stock room
# ---------------------------
selected_stock = st.selectbox("Select Stock Room", user_stocks)
st.markdown(f"### 💬 Chat for {selected_stock}")

# ---------------------------
# Auto-refresh chat
# ---------------------------
st_autorefresh(interval=5000, key=f"refresh_{selected_stock}")

# ---------------------------
# Chat input form (safe, clears automatically)
# ---------------------------
with st.form(key="chat_form", clear_on_submit=True):
    message_input = st.text_input("Type your message:")
    send_btn = st.form_submit_button("Send")

    if send_btn and message_input.strip():
        supabase.table("stock_chats").insert({
            "stock_symbol": selected_stock,
            "user_id": user_id,
            "message": message_input.strip(),
            "created_at": datetime.now(pytz.UTC).isoformat()
        }).execute()
        st.rerun()

# ---------------------------
# Fetch last 50 messages
# ---------------------------
messages_resp = supabase.table("stock_chats") \
    .select("user_id, message, created_at") \
    .eq("stock_symbol", selected_stock) \
    .order("created_at", desc=True) \
    .limit(50).execute()

messages = messages_resp.data[::-1] if messages_resp.data else []

# ---------------------------
# Chat bubbles CSS
# ---------------------------
st.markdown("""
<style>
.chat-bubble {
    padding: 10px 15px;
    border-radius: 15px;
    margin: 5px 0;
    max-width: 70%;
    word-wrap: break-word;
}
.chat-user {
    background-color: #1f77b4;
    color: white;
}
.chat-other {
    background-color: #e0e0e0;
    color: black;
}
.chat-container {
    display: flex;
    flex-direction: column;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Display chat messages in scrollable container
# ---------------------------
st.markdown('<div id="chat-container" class="chat-container" style="overflow-y:auto; max-height:600px;">', unsafe_allow_html=True)

for msg in messages:
    # fetch user info
    user_resp = supabase.table("users").select("display_name, avatar_url").eq("user_id", msg["user_id"]).execute()
    user = user_resp.data[0] if user_resp.data else {"display_name": "Unknown", "avatar_url": None}
    display_name = user["display_name"]
    avatar_url = user.get("avatar_url")

    # parse timestamp from ISO string
    timestamp_str = msg.get("created_at")
    timestamp = ""
    if timestamp_str:
        try:
            dt = datetime.fromisoformat(timestamp_str)
            dt = dt.astimezone(pytz.UTC)
            timestamp = dt.strftime("%H:%M")
        except Exception:
            timestamp = timestamp_str

    # choose bubble class
    bubble_class = "chat-user" if msg["user_id"] == user_id else "chat-other"
    avatar_html = f'<img src="{avatar_url}" width="40" style="border-radius:50%;">' if avatar_url else '<img src="https://via.placeholder.com/40?text=U" width="40" style="border-radius:50%;">'

    safe_message = html.escape(msg['message'])
    safe_message = emoji.emojize(safe_message, language='alias')

    # Render Markdown in bubble
    st.markdown(f"""
    <div style="display:flex; align-items:flex-start;">
        <div>{avatar_html}</div>
        <div class="chat-bubble {bubble_class}" style="margin-left:10px;">
            <b>{display_name}</b> [{timestamp}]<br>
            {safe_message}
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# Auto-scroll to bottom
# ---------------------------
st.markdown("""
<script>
var chatContainer = document.getElementById('chat-container');
if (chatContainer) {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}
</script>
""", unsafe_allow_html=True)
