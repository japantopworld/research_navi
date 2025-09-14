from flask import Blueprint, render_template, request, redirect, url_for, session

# Blueprint を定義
auth_bp = Blueprint("auth_bp", __name__)

# 管理者アカウント
ADMIN_ID = "KING1219"
ADMIN_PASS = "11922960"


# -----------------------------
# ログイン
# -----------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        user_id = request.form.get("user_id")
        password = request.form.get("password")

        if user_id == ADMIN_ID and password == ADMIN_PASS:
            session["logged_in"] = True
            session["user_id"] = user_id
            return redirect(url_for("home"))
        else:
            error = "ID またはパスワードが間違っています"

    return render_template("pages/login.html", error=error)


# -----------------------------
# ログアウト
# -----------------------------
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth_bp.login"))


# -----------------------------
# 新規登録
# -----------------------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # 本来はユーザー登録処理をするが、今はログインへリダイレクト
        return redirect(url_for("auth_bp.login"))
    return render_template("pages/register.html")
