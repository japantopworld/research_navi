# routes/register.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
import csv
import os

register_bp = Blueprint("register_bp", __name__)

CSV_FILE = os.path.join("data", "users.csv")

@register_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_data = {
            "ユーザー名": request.form.get("username"),
            "ふりがな": request.form.get("kana"),
            "生年月日": request.form.get("birthday"),
            "年齢": request.form.get("age"),
            "電話番号": request.form.get("tel"),
            "携帯番号": request.form.get("mobile"),
            "メールアドレス": request.form.get("email"),
            "部署": request.form.get("department"),
            "職種": request.form.get("role"),
            "紹介者NO": request.form.get("intro_code"),
            "ID": request.form.get("login_id"),
            "PASS": request.form.get("password")
        }

        # ID重複チェック
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["ID"] == user_data["ID"]:
                        flash("このIDは既に使われています", "danger")
                        return redirect(url_for("register_bp.register"))

        # ヘッダー付きで追記
        file_exists = os.path.exists(CSV_FILE)
        with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=user_data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(user_data)

        flash("登録が完了しました。ログインしてください。", "success")
        return redirect(url_for("login_bp.login"))

    return render_template("auth/register.html")
