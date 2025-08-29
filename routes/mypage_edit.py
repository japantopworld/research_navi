from flask import Blueprint, render_template, request, session, redirect, url_for, flash
import csv
import os

mypage_edit_bp = Blueprint("mypage_edit_bp", __name__)
DATA_PATH = "data/users.csv"

ADMIN_ID = "KING1219"

@mypage_edit_bp.route("/mypage/edit", methods=["GET", "POST"])
def edit_mypage():
    if "user_info" not in session:
        return redirect(url_for("login_bp.login"))

    user_info = session["user_info"]

    # 管理者チェック
    if user_info.get("login_id") != ADMIN_ID:
        flash("このページにはアクセスできません。", "error")
        return redirect(url_for("mypage_bp.mypage"))

    if request.method == "POST":
        login_id = request.form.get("login_id")

        updated_data = {
            "username": request.form.get("username"),
            "kana": request.form.get("kana"),
            "birthday": request.form.get("birthday"),
            "age": request.form.get("age"),
            "tel": request.form.get("tel"),
            "mobile": request.form.get("mobile"),
            "email": request.form.get("email"),
            "department": request.form.get("department"),
            "intro_code": request.form.get("intro_code"),
        }

        # CSVを更新
        rows = []
        with open(DATA_PATH, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["ID"] == login_id:
                    row.update(updated_data)
                rows.append(row)

        with open(DATA_PATH, "w", newline='', encoding='utf-8') as csvfile:
            fieldnames = rows[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        flash("情報を更新しました。", "success")
        return redirect(url_for("mypage_bp.mypage"))

    return render_template("pages/mypage_edit.html", user_info=user_info)

