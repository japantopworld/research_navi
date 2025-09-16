from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import csv, os, random, string

login_bp = Blueprint("login_bp", __name__, url_prefix="/login")

USERS_CSV = "data/users.csv"

# 管理者固定ID
ADMIN_ID = "KING1219"
ADMIN_PASS = "11922960"

@login_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form.get("user_id")
        password = request.form.get("password")

        # 管理者ログイン
        if user_id == ADMIN_ID and password == ADMIN_PASS:
            session["logged_in"] = True
            session["user_id"] = user_id
            session["is_admin"] = True
            flash("管理者としてログインしました ✅", "success")
            return redirect(url_for("mypage_bp.mypage"))

        # 一般ユーザーログイン
        if os.path.exists(USERS_CSV):
            with open(USERS_CSV, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["ID"] == user_id and row["PASS"] == password:
                        session["logged_in"] = True
                        session["user_id"] = user_id
                        session["is_admin"] = False
                        flash("ログイン成功 ✅", "success")
                        return redirect(url_for("mypage_bp.mypage"))

        flash("IDまたはパスワードが違います ❌", "danger")

    return render_template("auth/login.html")


@login_bp.route("/logout")
def logout():
    session.clear()
    flash("ログアウトしました 👋", "info")
    return redirect(url_for("home"))


# 🔹 ID・パスワードを忘れた方
@login_bp.route("/forgot", methods=["GET", "POST"])
def forgot():
    message = None
    new_password = None

    if request.method == "POST":
        user_id = request.form.get("user_id")
        mode = request.form.get("mode")  # "id" or "password"

        if user_id == ADMIN_ID:
            message = "⚠ 管理者アカウントは対象外です。"
        elif not os.path.exists(USERS_CSV):
            message = "ユーザー登録データが存在しません。"
        else:
            rows = []
            found = False
            with open(USERS_CSV, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["ID"] == user_id:
                        found = True
                        if mode == "password":
                            # 新しいパスワード生成（8文字ランダム）
                            new_password = "".join(random.choices(string.ascii_letters + string.digits, k=8))
                            row["PASS"] = new_password
                        # ID 照会モードなら何もしない
                    rows.append(row)

            if found:
                # CSVを上書き保存（passwordリセット時のみ反映）
                with open(USERS_CSV, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows(rows)

                if mode == "id":
                    message = f"✅ あなたのIDは {user_id} です"
                elif mode == "password":
                    message = "✅ パスワードをリセットしました。新しいパスワードは下記に表示します。"
            else:
                message = "❌ 該当ユーザーが見つかりません。"

    return render_template("pages/forgot.html", message=message, new_password=new_password)
