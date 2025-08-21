from flask import Blueprint, render_template, request, redirect, flash
import csv
import os

register_bp = Blueprint("register", __name__)

@register_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("ユーザー名とパスワードは必須です。")
            return redirect("/register")

        file_path = "data/workers.csv"

        # 既存のユーザー名チェック
        if os.path.exists(file_path):
            with open(file_path, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and row[0] == username:
                        flash("このユーザー名は既に使われています。")
                        return redirect("/register")

        # 新規ユーザー登録
        with open(file_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([username, password])

        flash("登録が完了しました。ログインしてください。")
        return redirect("/login")

    return render_template("pages/register_worker.html")
