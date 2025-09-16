from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import csv
import os

login_bp = Blueprint("login_bp", __name__, url_prefix="/login")

# 管理者アカウント（ハードコード）
ADMIN_ID = "KING1219"
ADMIN_PASS = "11922960"

USERS_CSV = "data/users.csv"  # 一般ユーザー用CSV

@login_bp.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        user_id = request.form.get("user_id")
        password = request.form.get("password")

        # ① 管理者判定
        if user_id == ADMIN_ID and password == ADMIN_PASS:
            session["logged_in"] = True
            session["user_id"] = ADMIN_ID
            session["is_admin"] = True
            flash("管理者ログイン成功 ✅", "success")
            return redirect(url_for("mypage_bp.mypage"))

        # ② 一般ユーザー判定（CSV）
        if os.path.exists(USERS_CSV):
            with open(USERS_CSV, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["ID"] == user_id and row["PASS"] == password:
                        session["logged_in"] = True
                        session["user_id"] = user_id
                        session["is_admin"] = False
                        flash("ログイン成功 ✅", "success")
                        return redirect(url_for("mypage_bp.mypage"))

        error = "IDまたはパスワードが正しくありません。"

    return render_template("pages/login.html", error=error)


@login_bp.route("/logout")
def logout():
    session.clear()
    flash("ログアウトしました。", "info")
    return redirect(url_for("home"))
