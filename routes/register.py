from flask import Blueprint, render_template, request, redirect, url_for, flash
import csv
import os

register_bp = Blueprint("register_bp", __name__)

USERS_CSV = "data/users.csv"

@register_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        new_user = {
            "ユーザー名": request.form.get("username"),
            "ふりがな": request.form.get("furigana"),
            "生年月日": request.form.get("birthday"),
            "年齢": request.form.get("age"),
            "電話番号": request.form.get("tel"),
            "携帯番号": request.form.get("mobile"),
            "メールアドレス": request.form.get("email"),
            "部署": request.form.get("department"),
            "紹介者NO": request.form.get("referrer"),
            "ID": request.form.get("login_id"),
            "PASS": request.form.get("password")
        }

        file_exists = os.path.isfile(USERS_CSV)
        with open(USERS_CSV, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=new_user.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(new_user)

        flash("登録が完了しました。ログインしてください。", "success")
        return redirect(url_for("login_bp.login"))

    return render_template("auth/register.html")
