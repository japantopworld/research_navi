from flask import Blueprint, render_template, request, redirect, url_for, session, flash

login_bp = Blueprint("auth_bp", __name__)

# 管理者アカウント（直書き）
ADMIN_ID = "KING1219"
ADMIN_PASS = "11922960"

@login_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        user_id = request.form.get("user_id")
        password = request.form.get("password")

        if user_id == ADMIN_ID and password == ADMIN_PASS:
            session["logged_in"] = True
            session["user_id"] = user_id
            session["display_name"] = "管理者"
            flash("ログインに成功しました ✅")
            return redirect(url_for("mypage_bp.mypage"))
        else:
            error = "IDまたはパスワードが正しくありません ❌"

    return render_template("pages/login.html", error=error)

@login_bp.route("/logout")
def logout():
    session.clear()
    flash("ログアウトしました ✅")
    return redirect(url_for("auth_bp.login"))
