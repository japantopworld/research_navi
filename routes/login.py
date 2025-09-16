from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import csv, os, random, string

login_bp = Blueprint("login_bp", __name__, url_prefix="/login")

USERS_CSV = os.path.join("research_navi", "data", "users.csv")

# 管理者固定アカウント
ADMIN_ID = "KING1219"
ADMIN_PASS = "11922960"

# ✅ ログイン処理
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
            session["is_admin"] = True
            flash("管理者ログイン成功 ✅", "success")
            return redirect(url_for("mypage_bp.mypage"))

        # 一般ユーザーCSVチェック
        with open(USERS_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["ID"] == user_id and row["PASS"] == password:
                    session["logged_in"] = True
                    session["user_id"] = row["ID"]
                    session["is_admin"] = False
                    flash("ログイン成功 ✅", "success")
                    return redirect(url_for("mypage_bp.mypage"))

        error = "⚠️ ID またはパスワードが間違っています"
    return render_template("pages/login.html", error=error)


# ✅ ID・パスワード再発行（一般ユーザーのみ）
@login_bp.route("/forgot", methods=["GET", "POST"])
def forgot():
    new_pass = None
    found_user = None

    if request.method == "POST":
        user_id = request.form.get("user_id")
        email = request.form.get("email")

        # 管理者は対象外
        if user_id == ADMIN_ID:
            flash("⚠️ 管理者のパスワードは再発行できません。", "danger")
            return render_template("pages/forgot.html")

        users = []
        found = False

        with open(USERS_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["ID"] == user_id and row["メールアドレス"] == email:
                    new_pass = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                    row["PASS"] = new_pass
                    found = True
                    found_user = row
                users.append(row)

        if found:
            with open(USERS_CSV, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=users[0].keys())
                writer.writeheader()
                writer.writerows(users)

            flash("✅ 新しいパスワードを発行しました。", "success")
        else:
            flash("⚠️ 入力された情報が一致しません。", "danger")

    return render_template("pages/forgot.html", new_pass=new_pass, user=found_user)
