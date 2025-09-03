import random

def get_profit_items(min_rate=10, max_rate=20):
    dummy_items = []
    for i in range(10):
        buy_price = random.randint(1000, 5000)
        profit_rate = round(random.uniform(min_rate, max_rate), 2)
        sell_price = int(buy_price * (1 + profit_rate / 100))
        profit = sell_price - buy_price
        rotation_rate = round(random.uniform(1.0, 3.0), 2)

        dummy_items.append({
            "name": f"商品サンプル {i+1}",
            "buy_price": buy_price,
            "sell_price": sell_price,
            "profit": profit,
            "profit_rate": profit_rate,
            "rotation": rotation_rate,
        })
    return dummy_items
