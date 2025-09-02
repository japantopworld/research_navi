from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import csv
import os

login_bp = Blueprint("login_bp", __name__)
USER_CSV = "data/users.csv"

@login_bp.route("/", methods=["GET", "POST"])
@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_id = request.form["login_id"]
        password = request.form["password"]

        with open(USER_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["ID"] == login_id and row["PASS"] == password:
                    session["user_info"] = {
                        "username": row["ユーザー名"],
                        "kana": row["ユーザー名ふりがな"],
                        "birthday": row["生年月日"],
                        "age": row["年齢"],
                        "tel": row["電話番号"],
                        "mobile": row["携帯番号"],
                        "email": row["メールアドレス"],
                        "department": row["部署"],
                        "intro_code": row["紹介者NO"],
                        "login_id": row["ID"]
                    }
                    flash("ログイン成功しました")
                    return redirect(url_for("pages_bp.home"))

        flash("ログインに失敗しました")
        return redirect(url_for("login_bp.login"))

    return render_template("auth/login.html")

@login_bp.route("/logout")
def logout():
    session.clear()
    flash("ログアウトしました")
    return redirect(url_for("login_bp.login"))
