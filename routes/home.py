from flask import Blueprint, render_template, session, redirect, url_for, flash

home_bp = Blueprint("home_bp", __name__)

# トップページ（全体公開）
@home_bp.route("/")
def home():
    if "user_id" in session:
        user_name = session.get("user_name", "ゲスト")
        return render_template("pages/home.html", user_name=user_name)
    else:
        return render_template("pages/welcome.html")

# マイページ（自分だけが見れるページ）
@home_bp.route("/mypage")
def mypage():
    if "user_info" not in session:
        flash("ログインしてください。", "warning")
        return redirect(url_for("login_bp.login"))

    user_info = session["user_info"]
    return render_template("pages/mypage.html", user=user_info)
