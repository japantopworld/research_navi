from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import csv
import os

login_bp = Blueprint("login_bp", __name__, url_prefix="/login")

DATA_FILE = "data/users.csv"

# 管理者アカウント（固定）
ADMIN_ID = "KING1219"
ADMIN_PASS = "11922960"


@login_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form.get("user_id", "").strip()
        password = request.form.get("password", "").strip()

        # 管理者ログイン
        if user_id == ADMIN_ID and password == ADMIN_PASS:
            session["logged_in"] = True
            session["user_id"] = ADMIN_ID
            session["role"] = "admin"
            flash("管理者ログイン成功", "success")
            return redirect(url_for("mypage_bp.mypage"))

        # 一般ユーザーログイン（CSV確認）
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["ID"] == user_id and row["PASS"] == password:
                        session["logged_in"] = True
                        session["user_id"] = user_id
                        session["role"] = "user"
                        flash("ログイン成功", "success")
                        return redirect(url_for("mypage_bp.mypage"))

        flash("ID または パスワードが違います", "danger")

    return render_template("auth/login.html")


@login_bp.route("/logout")
def logout():
    session.clear()
    flash("ログアウトしました", "info")
    return redirect(url_for("home"))


@login_bp.route("/forgot", methods=["GET", "POST"])
def forgot():
    message = None
    if request.method == "POST":
        user_id = request.form.get("user_id", "").strip()
        new_pass = request.form.get("new_pass", "").strip()

        # 管理者は対象外
        if user_id == ADMIN_ID:
            message = {"type": "error", "text": "管理者アカウントは再発行できません"}
        elif os.path.exists(DATA_FILE):
            rows = []
            updated = False
            with open(DATA_FILE, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["ID"] == user_id:
                        row["PASS"] = new_pass
                        updated = True
                    rows.append(row)

            if updated:
                with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows(rows)
                message = {"type": "success", "text": f"✅ パスワードを再発行しました。新しいパスワード: {new_pass}"}
            else:
                message = {"type": "error", "text": "該当するユーザーが見つかりません"}

    return render_template("pages/forgot.html", message=message)
