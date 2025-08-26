# routes/login.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import csv
import os

login_bp = Blueprint("login_bp", __name__)

USERS_CSV_PATH = os.path.join("data", "users.csv")

@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_id = request.form["login_id"]
        password = request.form["password"]

        try:
            with open(USERS_CSV_PATH, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["ID"] == login_id and str(row["PASS"]) == password:
                        session["user_id"] = login_id
                        session["user_name"] = row["ユーザー名"]
                        session["user_info"] = {
                            "username": row["ユーザー名"],
                            "kana": row["ふりがな"],
                            "birthday": row["生年月日"],
                            "age": row["年齢"],
                            "tel": row["電話番号"],
                            "mobile": row["携帯番号"],
                            "email": row["メールアドレス"],
                            "department": row["部署"],
                            "intro_code": row["紹介者NO"],
                            "login_id": row["ID"]
                        }
                        flash("ログインに成功しました！", "success")
                        return redirect(url_for("home_bp.mypage"))

            flash("ログインIDまたはパスワードが違います", "danger")
            return redirect(url_for("login_bp.login"))

        except Exception as e:
            flash(f"エラーが発生しました: {str(e)}", "danger")
            return redirect(url_for("login_bp.login"))

    return render_template("auth/login.html")
