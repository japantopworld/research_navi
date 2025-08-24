from flask import Blueprint, render_template, session
from models.user_model import User

mypage_bp = Blueprint("mypage_bp", __name__, url_prefix="/mypage")

@mypage_bp.route("/")
def mypage():
    login_id = session.get("login_id")
    if not login_id:
        return "ログインしてください", 401

    user = User.query.filter_by(login_id=login_id).first()
    if not user:
        return "ユーザー情報が見つかりません", 404

    return render_template("pages/mypage.html", user=user)
