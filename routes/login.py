import csv
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

login_bp = Blueprint("login_bp", __name__, url_prefix="/login")

CSV_FILE = "data/users.csv"

@login_bp.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        user_id = request.form.get("user_id")
        password = request.form.get("password")

        # ✅ 管理者ログイン
        if user_id == "KING1219" and password == "11922960":
            session["logged_in"] = True
            session["user_id"] = "KING1219"
            flash("管理者としてログインしました ✅", "success")
            return redirect(url_for("mypage_bp.mypage"))

        # ✅ CSVから一般ユーザーを探す（IDベース）
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["ID"] == user_id and row["PASS"] == password:
                        session["logged_in"] = True
                        session["user_id"] = row["ID"]
                        session["username"] = row["ユーザー名"]
                        flash("ログイン成功 ✅", "success")
                        return redirect(url_for("mypage_bp.mypage"))

        # 失敗時
        error = "⚠️ ID またはパスワードが間違っています。"

    return render_template("pages/login.html", error=error)


@login_bp.route("/logout")
def logout():
    session.clear()
    flash("ログアウトしました 👋", "info")
    return redirect(url_for("home"))
