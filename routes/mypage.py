from flask import Blueprint, render_template, request
from utils.profit_finder import get_profit_items

mypage_bp = Blueprint("mypage_bp", __name__)

@mypage_bp.route("/mypage", methods=["GET", "POST"])
def mypage():
    min_profit_rate = float(request.form.get("min_profit_rate", 10))
    max_profit_rate = float(request.form.get("max_profit_rate", 20))
    items = get_profit_items(min_profit_rate, max_profit_rate)
    return render_template("pages/mypage.html", items=items, min_rate=min_profit_rate, max_rate=max_profit_rate)
