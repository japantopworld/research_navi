def calc_profit(sell_price, cost_price, fee_rate=0.1, shipping=500, cashback=0):
    fee = sell_price * fee_rate
    net_profit = sell_price - cost_price - fee - shipping + cashback
    roi = (net_profit / cost_price) * 100 if cost_price > 0 else 0
    return {
        "sell_price": sell_price,
        "cost_price": cost_price,
        "fee": fee,
        "shipping": shipping,
        "cashback": cashback,
        "net_profit": net_profit,
        "roi": roi
    }
