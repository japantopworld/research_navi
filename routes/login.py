from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import csv
import os

login_bp = Blueprint("login_bp", __name__)

USERS_CSV = "data/users.csv"

def read_users_csv():
    if not os.path.exists(USERS_CSV):
        return []
    with open(USERS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_id = request.form.get("login_id")
        password = request.form.get("password")

        users = read_users_csv()
        user = next((u for u in users if u["ID"] == login_id and u["PASS"] == password), None)

        if user:
            session["user_id"] = login_id
            session["user_name"] = user.get("ユーザー名", "未登録")
            return redirect(url_for("home"))  # ✅ 修正点：Blueprint名を外して直接 home 関数へ
        else:
            flash("ログインIDまたはパスワードが違います", "danger")

    return render_template("auth/login.html")
