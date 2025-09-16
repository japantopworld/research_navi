from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user import User

login_bp = Blueprint("login_bp", __name__, url_prefix="/login")

# 管理者アカウント（固定）
ADMIN_ID = "KING1219"
ADMIN_PASS = "11922960"

@login_bp.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        input_id = request.form.get("username")
        input_pass = request.form.get("password")

        # ✅ 管理者チェック
        if input_id == ADMIN_ID and input_pass == ADMIN_PASS:
            session["logged_in"] = True
            session["user_id"] = ADMIN_ID
            session["is_admin"] = True
            flash("👑 管理者ログイン成功！", "success")
            return redirect(url_for("mypage_bp.mypage"))

        # ✅ 一般ユーザー（DB検索）
        user = User.query.filter_by(username=input_id, password=input_pass).first()
        if user:
            session["logged_in"] = True
            session["user_id"] = user.username
            session["is_admin"] = False
            flash("✅ ログイン成功！", "success")
            return redirect(url_for("mypage_bp.mypage"))
        else:
            error = "❌ ID またはパスワードが違います。"

    return render_template("pages/login.html", error=error)

@login_bp.route("/logout")
def logout():
    session.clear()
    flash("↩ ログアウトしました。", "info")
    return redirect(url_for("login_bp.login"))
