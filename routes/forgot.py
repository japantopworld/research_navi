from flask import Blueprint, render_template, request, redirect, url_for, flash
import csv
import os

forgot_bp = Blueprint("forgot_bp", __name__, url_prefix="/forgot")

USERS_CSV = os.path.join("research_navi", "data", "users.csv")

# 🔑 IDを忘れた場合
@forgot_bp.route("/id", methods=["GET", "POST"])
def forgot_id():
    user_id = None
    error = None
    if request.method == "POST":
        email = request.form.get("email")
        if not os.path.exists(USERS_CSV):
            error = "ユーザーデータが存在しません。"
        else:
            with open(USERS_CSV, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["メールアドレス"] == email:
                        user_id = row["ID"]
                        break
            if not user_id:
                error = "一致するメールアドレスが見つかりません。"

    return render_template("pages/forgot_id.html", user_id=user_id, error=error)

# 🔒 パスワードを忘れた場合
@forgot_bp.route("/password", methods=["GET", "POST"])
def forgot_password():
    success = None
    error = None
    if request.method == "POST":
        user_id = request.form.get("user_id")
        email = request.form.get("email")
        new_pass = request.form.get("new_pass")

        if not os.path.exists(USERS_CSV):
            error = "ユーザーデータが存在しません。"
        else:
            rows = []
            found = False
            with open(USERS_CSV, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["ID"] == user_id and row["メールアドレス"] == email:
                        row["PASS"] = new_pass
                        found = True
                    rows.append(row)

            if found:
                with open(USERS_CSV, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows(rows)
                success = "パスワードを再設定しました。ログインしてください。"
            else:
                error = "ID または メールアドレスが一致しません。"

    return render_template("pages/forgot_password.html", success=success, error=error)
