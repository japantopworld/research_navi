# routes/pages.py

from flask import Blueprint, render_template, session

# Blueprint名を pages_bp に統一（home.htmlと一致）
pages_bp = Blueprint("pages_bp", __name__, url_prefix="/mypage")

@pages_bp.route("/")
def mypage():
    username = session.get("username", "ゲスト")
    return render_template("pages/mypage.html", username=username)
