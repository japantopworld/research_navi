from flask import Blueprint, render_template, request, flash, redirect, url_for
import csv, os, random, string

forgot_bp = Blueprint("forgot_bp", __name__, url_prefix="/forgot")

USERS_CSV = "data/users.csv"
ADMIN_ID = "KING1219"  # 管理者固定ID（対象外）

@forgot_bp.route("/", methods=["GET", "POST"])
def forgot():
    error_admin = False

    if request.method == "POST":
        email = request.form.get("email")
        birthday = request.form.get("birthday")
        action = request.form.get("action")

        if not os.path.exists(USERS_CSV):
            flash("ユーザー情報データベースが存在しません。", "error")
            return redirect(url_for("forgot_bp.forgot"))

        rows = []
        user_found = None

        # CSV 読み込み
        with open(USERS_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["メールアドレス"] == email and row["生年月日"] == birthday:
                    user_found = row
                rows.append(row)

        if not user_found:
            flash("該当するユーザーが見つかりませんでした。", "error")
            return redirect(url_for("forgot_bp.forgot"))

        # 管理者は対象外
        if user_found["ID"] == ADMIN_ID:
            error_admin = True
            return render_template("pages/forgot.html", error_admin=error_admin)

        # ID照会
        if action == "id":
            flash(f"🆔 ご登録のIDは 【{user_found['ID']}】 です。", "success")
            return redirect(url_for("forgot_bp.forgot"))

        # パスワード再発行
        if action == "pass":
            new_pass = "".join(random.choices(string.ascii_letters + string.digits, k=8))

            # CSV更新
            for row in rows:
                if row["ID"] == user_found["ID"]:
                    row["PASS"] = new_pass

            with open(USERS_CSV, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)

            flash(f"🔒 新しいパスワードは 【{new_pass}】 です。ログイン後に変更してください。", "success")
            return redirect(url_for("login_bp.login"))

    return render_template("pages/forgot.html", error_admin=error_admin)
