import streamlit as st
import pandas as pd
import plotly.express as px

CURRENCY_FORMAT = "₹{:.2f}"

def show_prices(prices):
    st.markdown("## 💹 Current Market Prices")
    df = pd.DataFrame(list(prices.items()), columns=["Color", "Price"])
    styled_df = df.style.format({"Price": CURRENCY_FORMAT})
    st.table(styled_df)

def show_portfolio(portfolio):
    st.markdown("## 📦 Your Portfolio")
    df = pd.DataFrame(list(portfolio.items()), columns=["Asset", "Amount"])
    styled_df = df.style.format({"Amount": CURRENCY_FORMAT})
    st.table(styled_df)

def show_trade_history(history):
    if not history:
        st.info("No trades made yet. Start trading to see history here.")
        return

    st.markdown("## 🗂️ Trade History")
    df = pd.DataFrame(history)
    df.index += 1
    df = df.rename_axis("Trade #").reset_index()

    styled_df = df.style.format({
        "Price": CURRENCY_FORMAT,
        "Cash": CURRENCY_FORMAT
    }).background_gradient(cmap="YlGnBu", axis=0)

    st.dataframe(styled_df, use_container_width=True)

def plot_portfolio_value(history, starting_cash):
    if not history:
        st.info("No trades to visualize yet.")
        return

    df = pd.DataFrame(history)
    df["Portfolio Value"] = df["Cash"]
    df["Trade"] = df.index + 1

    fig = px.line(
        df,
        x="Trade",
        y="Portfolio Value",
        markers=True,
        title="📈 Portfolio Value Over Time",
        template="plotly_dark" if st.get_option("theme.base") == "dark" else "plotly_white",
        labels={"Portfolio Value": "Value (₹)", "Trade": "Trade Number"}
    )
    fig.update_traces(line_color="#FF5733", marker=dict(size=8, color="#FFC300"))

    st.plotly_chart(fig, use_container_width=True)

def show_leaderboard(leaderboard):
    st.markdown("## 🏆 Global Leaderboard")
    if leaderboard.empty:
        st.warning("Leaderboard is empty. Be the first to record a top score!")
        return

    leaderboard = leaderboard.copy()
    leaderboard.index += 1
    leaderboard = leaderboard.rename_axis("Rank").reset_index()

    leaderboard["Score"] = leaderboard["Score"].apply(lambda x: f"₹{int(x):,}")

    st.dataframe(leaderboard, use_container_width=True)
