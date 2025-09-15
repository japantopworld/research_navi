from flask import Blueprint, render_template, request, session
from utils.profit_finder import get_profit_items

mypage_bp = Blueprint("mypage_bp", __name__)

@mypage_bp.route("/mypage", methods=["GET", "POST"])
def mypage():
    # 仮のログインユーザー情報（本番はDBやsessionから取得予定）
    user = {
        "ID": session.get("user_id", "guest123"),
        "メールアドレス": session.get("email", None),
        "部署": session.get("department", None),
        "紹介者NO": session.get("ref_code", None)
    }
    display_name = session.get("display_name", "ゲスト")

    # 利益フィルタ
    min_profit_rate = float(request.form.get("min_profit_rate", 10))
    max_profit_rate = float(request.form.get("max_profit_rate", 20))
    items = get_profit_items(min_profit_rate, max_profit_rate)

    return render_template(
        "pages/mypage.html",
        user=user,
        display_name=display_name,
        items=items,
        min_rate=min_profit_rate,
        max_rate=max_profit_rate
    )
