import json
import bcrypt
import os

USERS_FILE = os.path.join("database", "users.json")

def ensure_users_file():
    """
    Makes sure users.json exists and is valid.
    Creates an empty JSON object if missing or corrupt.
    """
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({}, f)
        return

    # Check if file is empty or invalid
    try:
        with open(USERS_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                raise ValueError("Empty file")
            json.loads(content)
    except (json.JSONDecodeError, ValueError):
        with open(USERS_FILE, "w") as f:
            json.dump({}, f)

def load_users():
    ensure_users_file()
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def signup(username, password):
    if not username or not password:
        return False, "⚠️ Username and password cannot be empty."

    users = load_users()
    if username in users:
        return False, "❌ Username already exists. Please choose another."
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users[username] = {
        "password": hashed_pw,
        "portfolio": None,
        "trade_history": []
    }
    save_users(users)
    return True, f"✅ Signup successful! Welcome, {username}."

def login(username, password):
    users = load_users()
    if username not in users:
        return False, "❌ User not found. Please sign up first."
    hashed_pw = users[username]["password"].encode()
    if bcrypt.checkpw(password.encode(), hashed_pw):
        return True, f"✅ Login successful! Welcome back, {username}."
    else:
        return False, "❌ Incorrect password. Please try again."

def load_user_data(username):
    users = load_users()
    user_data = users.get(username, {})
    return user_data.get("portfolio"), user_data.get("trade_history", [])

def save_user_data(username, portfolio, trade_history):
    users = load_users()
    if username in users:
        users[username]["portfolio"] = portfolio
        users[username]["trade_history"] = trade_history
        save_users(users)
