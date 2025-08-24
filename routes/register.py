from flask import Blueprint, render_template, request, redirect, url_for, flash
import csv
import os
from datetime import datetime

register_bp = Blueprint("register_bp", __name__)
USERS_CSV = "data/users.csv"

DEPARTMENTS = {
    "KIN": "鳳陽管理職（その他）",
    "BYR": "バイヤー",
    "KEI": "経理",
    "HAN": "販売員",
    "BUT": "物流",
    "GOT": "合統括"
}

def generate_login_id(department_code, birthday_str, intro_code_alpha):
    try:
        birthday = datetime.strptime(birthday_str, "%Y/%m/%d")
        mmdd = birthday.strftime("%m%d")
    except:
        return None

    if intro_code_alpha not in ["A", "B", "C", "D", "E"]:
        return None

    if not os.path.exists(USERS_CSV):
        existing = []
    else:
        with open(USERS_CSV, "r", encoding="utf-8") as f:
            existing = list(csv.DictReader(f))

    base = f"{department_code}{intro_code_alpha}{mmdd}"
    suffix_letter = intro_code_alpha
    similar_ids = [u["ID"] for u in existing if u["ID"].startswith(f"{base}{suffix_letter}")]
    serial = len(similar_ids) + 1
    return f"{base}{suffix_letter}{serial}"

@register_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        kana = request.form.get("kana")
        birthday = request.form.get("birthday")
        phone = request.form.get("phone")
        mobile = request.form.get("mobile")
        email = request.form.get("email")
        department = request.form.get("department")
        job_title = request.form.get("job_title")
        intro_code_alpha = request.form.get("intro_code")
        password = request.form.get("password")

        # バリデーション
        errors = []
        if not username: errors.append("ユーザー名が未入力です。")
        if not kana: errors.append("ふりがなが未入力です。")
        if not birthday: errors.append("生年月日が未入力です。")
        if not email: errors.append("メールアドレスが未入力です。")
        if not intro_code_alpha: errors.append("紹介者NOが未入力です。")
        if not password: errors.append("パスワードが未入力です。")
        if not phone and not mobile:
            errors.append("電話番号または携帯番号のいずれかを入力してください。")

        if errors:
            for error in errors:
                flash(error, "danger")
            return redirect(url_for("register_bp.register"))

        department_code = next((code for code, name in DEPARTMENTS.items() if name == department), "KIN")
        login_id = generate_login_id(department_code, birthday, intro_code_alpha)

        if not login_id:
            flash("ID生成に失敗しました。入力内容を確認してください。", "danger")
            return redirect(url_for("register_bp.register"))

        file_exists = os.path.exists(USERS_CSV)
        with open(USERS_CSV, "a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["ユーザー名", "ふりがな", "生年月日", "年齢", "電話番号", "携帯番号", "メールアドレス", "部署", "職種", "紹介者NO", "ID", "PASS"])
            age = datetime.today().year - datetime.strptime(birthday, "%Y/%m/%d").year
            writer.writerow([username, kana, birthday, age, phone, mobile, email, department, job_title, intro_code_alpha, login_id, password])

        flash(f"登録が完了しました。あなたのログインIDは {login_id} です。", "success")
        return redirect(url_for("login_bp.login"))

    return render_template("auth/register.html", departments=DEPARTMENTS.values(), intro_codes=["A", "B", "C", "D", "E"])
