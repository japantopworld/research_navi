from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import csv
import os

login_bp = Blueprint("login_bp", __name__, url_prefix="/login")

# ユーザーデータCSV
USERS_CSV = os.path.join("research_navi", "data", "users.csv")

# 管理者アカウント
ADMIN_ID = "KING1219"
ADMIN_PASS = "11922960"


# ログイン画面
@login_bp.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        user_id = request.form.get("user_id")
        password = request.form.get("password")

        # 管理者チェック
        if user_id == ADMIN_ID and password == ADMIN_PASS:
            session["logged_in"] = True
            session["user_id"] = ADMIN_ID
            flash("管理者でログインしました ✅", "success")
            return redirect(url_for("mypage_bp.mypage"))

        # CSVからユーザー確認
        if os.path.exists(USERS_CSV):
            with open(USERS_CSV, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["ID"] == user_id and row["PASS"] == password:
                        session["logged_in"] = True
                        session["user_id"] = row["ID"]
                        flash("ログイン成功 ✅", "success")
                        return redirect(url_for("mypage_bp.mypage"))

        error = "IDまたはパスワードが違います ❌"

    return render_template("pages/login.html", error=error)


# ログアウト
@login_bp.route("/logout")
def logout():
    session.clear()
    flash("ログアウトしました 👋", "info")
    return redirect(url_for("login_bp.login"))


# ID照会処理
@login_bp.route("/forgot/id", methods=["POST"])
def forgot_id():
    email = request.form.get("email")
    birthdate = request.form.get("birthdate")

    if os.path.exists(USERS_CSV):
        with open(USERS_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["メールアドレス"] == email and row["生年月日"] == birthdate:
                    flash(f"✅ あなたの登録IDは 【{row['ID']}】 です。", "success")
                    return redirect(url_for("login_bp.login"))

    flash("❌ 入力された情報ではIDを特定できませんでした。", "danger")
    return redirect(url_for("login_bp.login"))


# パスワード再発行処理（ダミー実装）
@login_bp.route("/forgot/password", methods=["POST"])
def forgot_password():
    user_id = request.form.get("user_id")
    email = request.form.get("email")

    if os.path.exists(USERS_CSV):
        with open(USERS_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["ID"] == user_id and row["メールアドレス"] == email:
                    # 本来はメール送信で再発行リンクを送る
                    flash("✅ パスワード再発行リンクをメールに送信しました。", "success")
                    return redirect(url_for("login_bp.login"))

    flash("❌ 入力された情報が一致しませんでした。", "danger")
    return redirect(url_for("login_bp.login"))
