# routes/auth.py

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import csv
import os

auth_bp = Blueprint("auth_bp", __name__)

# CSVファイルパス
USERS_CSV = "data/users.csv"  # 必ずこのパスにあること！

# ログイン画面（GET + POST）
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        input_id = request.form.get("user_id")
        input_pass = request.form.get("password")

        # 認証処理（CSVから照合）
        if os.path.exists(USERS_CSV):
            with open(USERS_CSV, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["ID"] == input_id and row["PASS"] == input_pass:
                        session["user_info"] = row  # セッションに保存
                        return redirect(url_for("home_bp.mypage"))
        flash("IDまたはパスワードが間違っています")
        return redirect(url_for("auth_bp.login"))

    return render_template("auth/login.html")


# 新規登録画面（GET + POST）
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        new_user = {
            "ユーザー名": request.form.get("username"),
            "ふりがな": request.form.get("furigana"),
            "生年月日": request.form.get("birthday"),
            "年齢": request.form.get("age"),
            "電話番号": request.form.get("phone"),
            "携帯番号": request.form.get("mobile"),
            "メールアドレス": request.form.get("email"),
            "部署": request.form.get("department"),
            "紹介者NO": request.form.get("referrer"),
            "ID": request.form.get("user_id"),
            "PASS": request.form.get("password"),
        }

        file_exists = os.path.exists(USERS_CSV)
        with open(USERS_CSV, "a", newline="", encoding="utf-8") as f:
            fieldnames = list(new_user.keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()
            writer.writerow(new_user)

        flash("登録が完了しました。ログインしてください。")
        return redirect(url_for("auth_bp.login"))

    return render_template("auth/register.html")
