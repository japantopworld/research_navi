from flask import Blueprint, render_template, request, redirect, url_for, session, flash

login_bp = Blueprint("login_bp", __name__, url_prefix="/login")

# 管理者アカウント
ADMIN_ID = "KING1219"
ADMIN_PASS = "11922960"

@login_bp.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        user_id = request.form.get("user_id")
        password = request.form.get("password")

        # 管理者ログイン
        if user_id == ADMIN_ID and password == ADMIN_PASS:
            session["logged_in"] = True
            session["user_id"] = ADMIN_ID
            session["is_admin"] = True
            flash("管理者ログイン成功", "success")
            return redirect(url_for("mypage_bp.mypage"))

        # TODO: 一般ユーザーの認証処理を追加
        error = "IDまたはパスワードが間違っています。"

    return render_template("pages/login.html", error=error)


# 🔑 ID・パスワードを忘れた方ページ
@login_bp.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        email = request.form.get("email")
        # TODO: 本来はデータベースからユーザー検索して処理
        flash(f"入力されたメールアドレス {email} に確認手順を送信しました（仮処理）。", "info")
        return redirect(url_for("login_bp.login"))

    return render_template("pages/forgot.html")
