from flask import Blueprint, render_template, session, redirect, url_for

mypage_bp = Blueprint("mypage_bp", __name__, url_prefix="/mypage")

@mypage_bp.route("/", methods=["GET"])
def mypage():
    if not session.get("logged_in"):
        return redirect(url_for("login_bp.login"))

    # 管理者 or 一般ユーザーを区別
    if session.get("user_id") == "KING1219":
        display_name = "管理者"
    else:
        display_name = session.get("username", session.get("user_id"))

    return render_template("pages/mypage.html", display_name=display_name)
