def calc_profit(cost, price, shipping=0, fee_pct=10.0, rebate_pct=0.0, coupon=0.0):
    rebate = cost * (rebate_pct/100.0)
    net_cost = max(0, cost - rebate - coupon)
    fee = price * (fee_pct/100.0)
    profit = price - fee - shipping - net_cost
    return {"net_cost":int(net_cost),"profit":int(profit),"margin_pct":round(100*profit/price,2) if price else 0,"roi_pct":round(100*profit/net_cost,2) if net_cost else 0}
