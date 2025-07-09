import streamlit as st
import json
import time

from auth import login, signup, load_user_data, save_user_data
from trading_engine import (
    initialize_prices,
    simulate_price_changes,
    random_market_event,
    execute_trade
)
from utils import update_leaderboard, get_leaderboard, calculate_portfolio_value
import dashboard

# ================================
# Load Configuration
# ================================
with open("config.json") as f:
    CONFIG = json.load(f)

GAME_SETTINGS = CONFIG["game_settings"]
STARTING_CASH = GAME_SETTINGS["starting_cash"]
MAX_TRADES = GAME_SETTINGS["max_trades"]

COLOR_NAMES = [c["name"] for c in CONFIG["colors"]]
COLOR_EMOJIS = {c["name"]: c["emoji"] for c in CONFIG["colors"]}

# ================================
# Page Settings
# ================================
st.set_page_config(
    page_title="🎨 Color Exchange Pro",
    page_icon="🎨",
    layout="wide"
)

# ================================
# Global Styling
# ================================
st.markdown("""
    <style>
        .stTabs [data-baseweb="tab-list"] button {
            font-size: 16px;
            padding: 8px 16px;
        }
        .stButton>button {
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown(
    "<h1 style='text-align: center; color: #E64A19;'>🎨 Color Exchange Pro</h1>",
    unsafe_allow_html=True
)
st.markdown("<p style='text-align: center;'>A fun, advanced trading simulator with real-time color markets 🚀</p>", unsafe_allow_html=True)
st.divider()

# ================================
# Session State Initialization
# ================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.portfolio = None
    st.session_state.trade_history = None
    st.session_state.prices = None
    st.session_state.trade_count = 0
    st.session_state.game_over = False

# ================================
# Authentication UI
# ================================
if not st.session_state.logged_in:
    st.subheader("👤 Welcome! Please log in or sign up to play")
    tabs = st.tabs(["🔐 Login", "📝 Sign Up"])

    with tabs[0]:
        login_user = st.text_input("Username", key="login_user")
        login_pass = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            success, message = login(login_user, login_pass)
            if success:
                st.session_state.logged_in = True
                st.session_state.username = login_user
                st.success(message)
                time.sleep(0.5)
                st.experimental_rerun()
            else:
                st.error(message)

    with tabs[1]:
        new_user = st.text_input("Choose Username", key="signup_user")
        new_pass = st.text_input("Choose Password", type="password", key="signup_pass")
        if st.button("Sign Up"):
            success, message = signup(new_user, new_pass)
            if success:
                st.success(message)
            else:
                st.error(message)

# ================================
# Authenticated Dashboard
# ================================
else:
    st.sidebar.header(f"✅ Logged in as: {st.session_state.username}")

    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.experimental_rerun()

    # Game State Setup
    if st.session_state.portfolio is None:
        st.session_state.prices = initialize_prices(COLOR_NAMES)
        st.session_state.portfolio = {"Cash": STARTING_CASH, **{c: 0 for c in COLOR_NAMES}}
        st.session_state.trade_history = []
        st.session_state.trade_count = 0
        st.session_state.game_over = False

    # Game Over Handling
    if st.session_state.game_over:
        st.warning("⚠️ Game Over! You've reached the maximum number of trades.")
        final_value = calculate_portfolio_value(st.session_state.portfolio, st.session_state.prices)
        st.success(f"🎯 Final Portfolio Value: ₹{final_value:,.2f}")

        update_leaderboard(st.session_state.username, final_value)
        save_user_data(st.session_state.username, st.session_state.portfolio, st.session_state.trade_history)

        if st.button("🔄 Restart Game"):
            st.session_state.prices = initialize_prices(COLOR_NAMES)
            st.session_state.portfolio = {"Cash": STARTING_CASH, **{c: 0 for c in COLOR_NAMES}}
            st.session_state.trade_history = []
            st.session_state.trade_count = 0
            st.session_state.game_over = False
            st.experimental_rerun()

    else:
        # Sidebar Trading Controls
        st.sidebar.subheader("🎮 Trading Controls")
        selected = st.sidebar.selectbox(
            "Select Color to Trade",
            [f"{COLOR_EMOJIS[c]} {c}" for c in COLOR_NAMES]
        )
        selected_color = selected.split(" ", 1)[1]

        quantity = st.sidebar.slider("Quantity", 1, 100, 1)
        action = st.sidebar.radio("Action", ["Buy", "Sell"], horizontal=True)

        if st.sidebar.button("✅ Execute Trade"):
            success, message = execute_trade(
                st.session_state.portfolio,
                action,
                selected_color,
                quantity,
                st.session_state.prices[selected_color]
            )
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
            st.sidebar.info(message)

    # ================================
    # Main Dashboard
    # ================================
    col1, col2 = st.columns(2)
    with col1:
        dashboard.show_prices(st.session_state.prices)
    with col2:
        dashboard.show_portfolio(st.session_state.portfolio)

    st.divider()
    dashboard.show_trade_history(st.session_state.trade_history)
    dashboard.plot_portfolio_value(st.session_state.trade_history, STARTING_CASH)
    leaderboard = get_leaderboard()
    dashboard.show_leaderboard(leaderboard)
