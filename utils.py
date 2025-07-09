import pandas as pd
from datetime import datetime
import os

LEADERBOARD_FILE = os.path.join("database", "leaderboard.csv")
MAX_LEADERBOARD_ENTRIES = 20

def update_leaderboard(username, score):
    """
    Add or update a user's score on the leaderboard with timestamp.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_entry = pd.DataFrame([{
        "Username": username,
        "Score": int(score),
        "Date": now
    }])

    if os.path.exists(LEADERBOARD_FILE):
        try:
            df = pd.read_csv(LEADERBOARD_FILE)
            df = pd.concat([df, new_entry], ignore_index=True)
        except Exception:
            df = new_entry
    else:
        df = new_entry

    # Keep top scores only
    df = df.sort_values(by="Score", ascending=False)
    df = df.head(MAX_LEADERBOARD_ENTRIES)
    df.to_csv(LEADERBOARD_FILE, index=False)

def get_leaderboard():
    """
    Load the leaderboard sorted by score.
    """
    if not os.path.exists(LEADERBOARD_FILE):
        return pd.DataFrame(columns=["Username", "Score", "Date"])

    try:
        df = pd.read_csv(LEADERBOARD_FILE)
        if "Date" not in df.columns:
            df["Date"] = ""
        return df.sort_values(by="Score", ascending=False)
    except Exception:
        return pd.DataFrame(columns=["Username", "Score", "Date"])

def calculate_portfolio_value(portfolio, prices):
    """
    Calculate total portfolio value with live prices.
    """
    value = portfolio["Cash"]
    for color in prices:
        value += portfolio[color] * prices[color]
    return value
