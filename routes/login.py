from flask import Blueprint, render_template, request, redirect, url_for, session

# Blueprint を login_bp で定義
login_bp = Blueprint("login_bp", __name__, url_prefix="/login")

# 管理者アカウント（直書き）
ADMIN_ID = "KING1219"
ADMIN_PASS = "11922960"

# ログインページ
@login_bp.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        user_id = request.form.get("user_id")
        password = request.form.get("password")

        # 管理者ログイン判定
        if user_id == ADMIN_ID and password == ADMIN_PASS:
            session["user"] = "admin"
            return redirect(url_for("home"))

        # TODO: 将来的に CSV / DB のユーザー認証を追加可能
        error = "IDまたはパスワードが違います"

    # login.html が templates/auth/login.html にある前提
    return render_template("auth/login.html", error=error)

# ログアウト
@login_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# 新規登録ページ（仮実装）
@login_bp.route("/register", methods=["GET", "POST"])
def register():
    # templates/auth/register.html を表示する前提
    return render_template("auth/register.html")
