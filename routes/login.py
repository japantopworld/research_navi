from flask import Blueprint, render_template, request, redirect, url_for, session
import csv
import os

login_bp = Blueprint("login_bp", __name__)

# 管理者アカウント（直書き）
ADMIN_ID = "KING1192"
ADMIN_PASS = "11922960"

@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_id = request.form["login_id"]
        password = request.form["password"]

        # ✅ 管理者チェック
        if login_id == ADMIN_ID and password == ADMIN_PASS:
            session["user_id"] = login_id
            return redirect(url_for("home"))

        # ✅ 一般ユーザー（CSV認証）
        if os.path.exists("users.csv"):
            with open("users.csv", newline="") as f:
                reader = csv.reader(f)
                for row in reader:
                    if row[0] == login_id and row[1] == password:
                        session["user_id"] = login_id
                        return redirect(url_for("home"))

        return "❌ IDまたはパスワードが間違っています。"

    return render_template("pages/login.html")

@login_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
