from flask import Blueprint, render_template, request, redirect, url_for
import csv
import os

register_bp = Blueprint("register_bp", __name__)
USER_CSV_PATH = "data/users.csv"

@register_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        form = request.form
        user_data = {
            "ユーザー名": form["username"],
            "ふりがな": form["furigana"],
            "生年月日": form["birthdate"],
            "年齢": form["age"],
            "電話番号": form["tel"],
            "携帯番号": form["mobile"],
            "メールアドレス": form["email"],
            "部署": form["department"],
            "紹介者NO": form["ref_code"][1:] if form["ref_code"].startswith("K") else form["ref_code"],
            "ID": form["birthdate"].replace("-", "")[4:] + form["ref_code"][1:] if form["ref_code"].startswith("K") else form["ref_code"],
            "PASS": form["password"]
        }

        write_header = not os.path.exists(USER_CSV_PATH)
        with open(USER_CSV_PATH, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=user_data.keys())
            if write_header:
                writer.writeheader()
            writer.writerow(user_data)

        return redirect(url_for("login_bp.login"))

    return render_template("pages/register_user.html")
