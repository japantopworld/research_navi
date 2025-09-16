from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import csv, os, random, string

login_bp = Blueprint("login_bp", __name__, url_prefix="/login")

# CSVファイルの場所
USERS_CSV = os.path.join("research_navi", "data", "users.csv")

# 管理者アカウント
ADMIN_ID = "KING1219"
ADMIN_PASS = "11922960"

# ログイン処理
@login_bp.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        user_id = request.form.get("user_id")
        password = request.form.get("password")

        # 管理者チェック
        if user_id == ADMIN_ID and password == ADMIN_PASS:
            session["logged_in"] = True
            session["user_id"] = user_id
            session["is_admin"] = True
            return redirect(url_for("mypage_bp.mypage"))

        # CSVユーザー照合
        if os.path.exists(USERS_CSV):
            with open(USERS_CSV, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["ID"] == user_id and row["PASS"] == password:
                        session["logged_in"] = True
                        session["user_id"] = user_id
                        session["is_admin"] = False
                        return redirect(url_for("mypage_bp.mypage"))

        error = "ID または パスワードが間違っています。"

    return render_template("pages/login.html", error=error)


# パスワード再発行
@login_bp.route("/forgot", methods=["GET", "POST"])
def forgot():
    popup_message = None
    new_pass = None

    if request.method == "POST":
        user_id = request.form.get("user_id")

        # 管理者は対象外
        if user_id == ADMIN_ID:
            popup_message = "⚠️ 管理者アカウントは対象外です。"
        else:
            if os.path.exists(USERS_CSV):
                rows = []
                updated = False
                with open(USERS_CSV, newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row["ID"] == user_id:
                            # 新しいパスワードを生成（8桁ランダム）
                            new_pass = "".join(random.choices(string.ascii_letters + string.digits, k=8))
                            row["PASS"] = new_pass
                            updated = True
                        rows.append(row)

                # CSVを上書き保存
                if updated:
                    with open(USERS_CSV, "w", newline="", encoding="utf-8") as f:
                        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                        writer.writeheader()
                        writer.writerows(rows)
                else:
                    popup_message = "❌ 入力されたIDは存在しません。"

    return render_template("pages/forgot.html", popup_message=popup_message, new_pass=new_pass)
