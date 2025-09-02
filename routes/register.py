from flask import Blueprint, render_template, request, redirect, url_for, flash
import csv
import os

register_bp = Blueprint("register_bp", __name__)
USER_CSV = "data/users.csv"

@register_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = {
            "ユーザー名": request.form["username"],
            "ユーザー名ふりがな": request.form["kana"],
            "生年月日": request.form["birthday"],
            "年齢": request.form["age"],
            "電話番号": request.form["tel"],
            "携帯番号": request.form["mobile"],
            "メールアドレス": request.form["email"],
            "部署": request.form["department"],
            "紹介者NO": request.form["intro_code"],
            "ID": request.form["login_id"],
            "PASS": request.form["password"]
        }

        file_exists = os.path.isfile(USER_CSV)
        with open(USER_CSV, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)

        flash("新規登録が完了しました。ログインしてください。")
        return redirect(url_for("login_bp.login"))

    return render_template("auth/register.html")
