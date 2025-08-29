from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import csv
import os

login_bp = Blueprint("login_bp", __name__)

# ユーザーCSVファイルのパス
USER_CSV = "data/users.csv"

# 管理者ID・パスワード（直書き）
ADMIN_ID = "KING1219"
ADMIN_PASS = "11922960"

@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_id = request.form["login_id"]
        password = request.form["password"]

        if login_id == ADMIN_ID and password == ADMIN_PASS:
            session["user_info"] = {
                "username": "管理者",
                "login_id": ADMIN_ID,
                "is_admin": True
            }
            return redirect(url_for("mypage_bp.mypage"))

        # 一般ユーザーのログイン判定
        if os.path.exists(USER_CSV):
            with open(USER_CSV, newline='', encoding='utf-8') as f:
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
                            "login_id": row["ID"],
                            "is_admin": False
                        }
                        return redirect(url_for("mypage_bp.mypage"))

        flash("ログインに失敗しました。IDまたはパスワードが間違っています。", "danger")

    return render_template("auth/login.html")


@login_bp.route("/logout")
def logout():
    session.pop("user_info", None)
    return redirect(url_for("login_bp.login"))
