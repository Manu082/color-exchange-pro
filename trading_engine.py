import random

def initialize_prices(colors):
    """
    Set starting price of ₹100 for each color.
    """
    return {color: 100 for color in colors}

def simulate_price_changes(prices):
    """
    Apply ±10% random volatility to each color's price.
    """
    updated_prices = {}
    for color, price in prices.items():
        change_pct = random.uniform(-0.10, 0.10)  # -10% to +10%
        new_price = max(10, int(price * (1 + change_pct)))
        updated_prices[color] = new_price
    return updated_prices

def random_market_event(prices):
    """
    Occasionally trigger a major market event that shifts prices.
    """
    events = [
        ("🔥 Demand surge for Red!", {"Red": +15}),
        ("🧊 Blue dye shortage hits market", {"Blue": +12}),
        ("🌿 Green pigment oversupply", {"Green": -10}),
        ("📉 Market-wide correction", {"Red": -8, "Blue": -8, "Green": -8}),
        ("💥 Red bubble burst!", {"Red": -20}),
        ("📈 All colors spike!", {"Red": +10, "Blue": +10, "Green": +10}),
    ]
    if random.random() < 0.3:
        event = random.choice(events)
        for color, change in event[1].items():
            prices[color] = max(10, prices[color] + change)
        return event[0]  # return event description
    return None

def execute_trade(portfolio, action, color, quantity, price):
    """
    Execute a Buy or Sell order for the user portfolio.
    """
    total_cost = quantity * price

    if action == "Buy":
        if portfolio["Cash"] >= total_cost:
            portfolio["Cash"] -= total_cost
            portfolio[color] += quantity
            return True, f"✅ Bought {quantity} of {color} at ₹{price}."
        else:
            return False, "❌ Insufficient funds to complete purchase."

    elif action == "Sell":
        if portfolio[color] >= quantity:
            portfolio[color] -= quantity
            portfolio["Cash"] += total_cost
            return True, f"✅ Sold {quantity} of {color} at ₹{price}."
        else:
            return False, f"❌ You don’t own enough {color} to sell."

    return False, "❌ Invalid action. Please choose Buy or Sell."
