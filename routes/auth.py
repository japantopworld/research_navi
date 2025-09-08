# routes/auth.py

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form.get("user_id")
        password = request.form.get("password")
        # 仮の認証（本番はCSVやDBと照合）
        if user_id == "testuser" and password == "testpass":
            session["user_id"] = user_id
            return redirect(url_for("home_bp.mypage"))
        flash("IDまたはパスワードが正しくありません。")
    return render_template("auth/login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # ユーザー登録処理（省略：CSV保存など）
        flash("登録が完了しました。ログインしてください。")
        return redirect(url_for("auth_bp.login"))
    return render_template("auth/register.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth_bp.login"))
