from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user import User
from utils.user_sync import sync_csv_to_db

login_bp = Blueprint("login_bp", __name__, url_prefix="/login")

# 管理者固定ID
ADMIN_ID = "KING1219"
ADMIN_PASS = "11922960"

@login_bp.route("/", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # CSV→DB 同期（新規追加分を反映）
        sync_csv_to_db()

        # 管理者チェック
        if username == ADMIN_ID and password == ADMIN_PASS:
            session["logged_in"] = True
            session["user_id"] = username
            flash("👑 管理者ログイン成功！", "success")
            return redirect(url_for("mypage_bp.mypage"))

        # 一般ユーザー認証
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session["logged_in"] = True
            session["user_id"] = user.username
            flash("✅ ログイン成功！", "success")
            return redirect(url_for("mypage_bp.mypage"))
        else:
            error = "⚠️ ユーザー名またはパスワードが間違っています"

    return render_template("pages/login.html", error=error)


@login_bp.route("/logout")
def logout():
    session.clear()
    flash("↩️ ログアウトしました。", "info")
    return redirect(url_for("login_bp.login"))
