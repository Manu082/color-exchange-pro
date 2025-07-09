import streamlit as st
import json

from auth import login, signup, load_user_data, save_user_data
from trading_engine import initialize_prices, simulate_price_changes, random_market_event, execute_trade
from utils import update_leaderboard, get_leaderboard, calculate_portfolio_value
import dashboard

# ===============================
# Load Config
# ===============================
with open("config.json") as f:
    CONFIG = json.load(f)

# Extract structured config
GAME_SETTINGS = CONFIG["game_settings"]
STARTING_CASH = GAME_SETTINGS["starting_cash"]
MAX_TRADES = GAME_SETTINGS["max_trades"]

# Colors list and emoji mapping
COLOR_NAMES = [c["name"] for c in CONFIG["colors"]]
COLOR_EMOJIS = {c["name"]: c["emoji"] for c in CONFIG["colors"]}

st.set_page_config(
    page_title="🎨 Color Exchange Pro",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# Theming
# ===============================
st.markdown("""
<style>
.sidebar .sidebar-content {
    background-color: #f8f9fa;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    "<h1 style='text-align: center; color: #FF5733;'>🎨 Color Exchange Pro — Advanced Trading Simulator</h1>",
    unsafe_allow_html=True
)

# ===============================
# Session Management
# ===============================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

# ===============================
# Login / Signup UI
# ===============================
if not st.session_state.logged_in:
    login_tab, signup_tab = st.tabs(["🔐 Login", "📝 Signup"])

    with login_tab:
        st.subheader("Login to your account")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", use_container_width=True):
            success, msg = login(username, password)
            st.info(msg)
            if success:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.experimental_rerun()

    with signup_tab:
        st.subheader("Create a new account")
        new_user = st.text_input("New Username", key="signup_user")
        new_pass = st.text_input("New Password", type="password", key="signup_pass")
        if st.button("Signup", use_container_width=True):
            success, msg = signup(new_user, new_pass)
            st.info(msg)

# ===============================
# Authenticated UI
# ===============================
else:
    st.sidebar.success(f"✅ Logged in as **{st.session_state.username}**")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.experimental_rerun()

    # Initialize Session State
    if "prices" not in st.session_state:
        st.session_state.prices = initialize_prices(COLOR_NAMES)
    if "portfolio" not in st.session_state:
        st.session_state.portfolio = {"Cash": STARTING_CASH, **{c: 0 for c in COLOR_NAMES}}
    if "trade_history" not in st.session_state:
        st.session_state.trade_history = []
    if "trade_count" not in st.session_state:
        st.session_state.trade_count = 0
    if "game_over" not in st.session_state:
        st.session_state.game_over = False

    # Sidebar Trading Panel
    st.sidebar.header("🎮 Trading Control Panel")

    if st.session_state.game_over:
        st.sidebar.warning("⚠️ Game Over! You've reached the max number of trades.")
        st.sidebar.markdown(f"**Total Trades:** {st.session_state.trade_count}")
        final_value = calculate_portfolio_value(st.session_state.portfolio, st.session_state.prices)
        st.sidebar.markdown(f"**Final Portfolio Value:** ₹{final_value:,.2f}")

        st.sidebar.markdown("---")
        if st.sidebar.button("🔄 Restart Game", use_container_width=True):
            st.session_state.clear()
            st.experimental_rerun()
    else:
        # Use emoji in dropdown
        color_options = [f"{COLOR_EMOJIS[c]} {c}" for c in COLOR_NAMES]
        selected_display = st.sidebar.selectbox("🎨 Select Color to Trade", color_options)
        selected_color = selected_display.split(" ", 1)[1]

        quantity = st.sidebar.number_input("Quantity", min_value=1, max_value=100, value=1, step=1)
        action = st.sidebar.radio("Action", ["Buy", "Sell"], horizontal=True)

        if st.sidebar.button("✅ Execute Trade", use_container_width=True):
            success, msg = execute_trade(
                st.session_state.portfolio,
                action,
                selected_color,
                quantity,
                st.session_state.prices[selected_color]
            )
            st.sidebar.info(msg)
            if success:
                st.session_state.trade_count += 1
                st.session_state.trade_history.append({
                    "Action": action,
                    "Color": selected_color,
                    "Quantity": quantity,
                    "Price": st.session_state.prices[selected_color],
                    "Cash": st.session_state.portfolio["Cash"]
                })

                st.session_state.prices = simulate_price_changes(st.session_state.prices)
                event = random_market_event(st.session_state.prices)
                if event:
                    st.sidebar.info(f"📰 Market News: {event}")

                if st.session_state.trade_count >= MAX_TRADES:
                    st.session_state.game_over = True
                    final_value = calculate_portfolio_value(st.session_state.portfolio, st.session_state.prices)
                    update_leaderboard(st.session_state.username, final_value)
                    save_user_data(st.session_state.username, st.session_state.portfolio, st.session_state.trade_history)

    # ===============================
    # Main Dashboard
    # ===============================
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            dashboard.show_prices(st.session_state.prices)
        with col2:
            dashboard.show_portfolio(st.session_state.portfolio)

        st.markdown("---")
        dashboard.show_trade_history(st.session_state.trade_history)
        dashboard.plot_portfolio_value(st.session_state.trade_history, STARTING_CASH)
        dashboard.show_leaderboard(get_leaderboard())
