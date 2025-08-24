from flask import Blueprint, render_template, request, redirect, url_for, flash
import csv
import os
from datetime import datetime

register_bp = Blueprint("register_bp", __name__)

# ✅ users.csv の保存先（dataフォルダ）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # /routes/
USERS_CSV = os.path.join(BASE_DIR, "..", "data", "users.csv")

# ✅ 部署名（略称 → フル名）
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
        email = request.form.get("email")
        department = request.form.get("department")
        intro_code_alpha = request.form.get("intro_code")
        password = request.form.get("password")
        tel = request.form.get("tel")
        mobile = request.form.get("mobile")

        # ✅ 入力チェック（どちらかは必須）
        if not tel and not mobile:
            flash("電話番号または携帯番号のいずれかを入力してください。", "danger")
            return redirect(url_for("register_bp.register"))

        # ✅ ログインID生成
        department_code = next((code for code, name in DEPARTMENTS.items() if name == department), "KIN")
        login_id = generate_login_id(department_code, birthday, intro_code_alpha)

        if not login_id:
            flash("登録情報に誤りがあります。部署・紹介コード・誕生日をご確認ください。", "danger")
            return redirect(url_for("register_bp.register"))

        # ✅ users.csv へ保存
        file_exists = os.path.exists(USERS_CSV)
        with open(USERS_CSV, "a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow([
                    "ユーザー名", "ふりがな", "生年月日", "年齢",
                    "電話番号", "携帯番号", "メールアドレス",
                    "部署", "紹介者NO", "ID", "PASS"
                ])
            age = datetime.today().year - datetime.strptime(birthday, "%Y/%m/%d").year
            writer.writerow([
                username, kana, birthday, age,
                tel, mobile, email,
                department, intro_code_alpha,
                login_id, password
            ])

        flash(f"登録が完了しました。あなたのログインIDは {login_id} です。", "success")
        return redirect(url_for("login_bp.login"))

    return render_template(
        "auth/register.html",
        departments=DEPARTMENTS.values(),
        intro_codes=["A", "B", "C", "D", "E"]
    )
