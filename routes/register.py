from flask import Blueprint, render_template, request, redirect, url_for, flash
import csv
import os
from datetime import datetime

register_bp = Blueprint("register_bp", __name__)

# 📁 保存先（Googleドライブ上にあるCSVファイルパス）
USERS_CSV = "data/users.csv"

# 部署一覧（表示名とコード）
DEPARTMENTS = {
    "KIN": "鳳陽管理職(その他)",
    "BYR": "バイヤー",
    "KEI": "経理",
    "HAN": "販売員",
    "BUT": "物流",
    "GOT": "合統括"
}

# 紹介コード（英字1文字）
VALID_INTRO_CODES = ["A", "B", "C", "D", "E"]

# ユーザーID生成（部署略号＋紹介コード＋MMDD＋連番）
def generate_login_id(department_code, birthday_str, intro_code_alpha):
    try:
        birthday = datetime.strptime(birthday_str, "%Y/%m/%d")
        mmdd = birthday.strftime("%m%d")
    except:
        return None

    if intro_code_alpha not in VALID_INTRO_CODES:
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

# 🔑 新規登録ルート
@register_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        kana = request.form.get("kana", "").strip()
        birthday = request.form.get("birthday", "").strip()
        phone = request.form.get("phone", "").strip()
        mobile = request.form.get("mobile", "").strip()
        email = request.form.get("email", "").strip()
        department = request.form.get("department", "").strip()
        job_title = request.form.get("job_title", "").strip()
        intro_code_alpha = request.form.get("intro_code", "").strip()
        password = request.form.get("password", "").strip()

        # ✅ 入力チェック
        errors = []

        if not username:
            errors.append("ユーザー名が未入力です。")
        if not kana:
            errors.append("ふりがなが未入力です。")
        try:
            birthday_dt = datetime.strptime(birthday, "%Y/%m/%d")
        except:
            errors.append("生年月日の形式が正しくありません（例：1990/01/01）。")
        if not phone:
            errors.append("電話番号が未入力です。")
        if not mobile:
            errors.append("携帯番号が未入力です。")
        if not email:
            errors.append("メールアドレスが未入力です。")
        if department not in DEPARTMENTS.values():
            errors.append("部署が正しく選択されていません。")
        if intro_code_alpha not in VALID_INTRO_CODES:
            errors.append("紹介者NOは A〜E のいずれかを選んでください。")
        if not password:
            errors.append("パスワードが未入力です。")

        # ❌ エラーがある場合はメッセージを出して戻す
        if errors:
            for err in errors:
                flash(err, "danger")
            return redirect(url_for("register_bp.register"))

        # ✅ 部署コード（例：BYRなど）を取得
        department_code = next((code for code, name in DEPARTMENTS.items() if name == department), "KIN")

        # ✅ ユーザーID生成
        login_id = generate_login_id(department_code, birthday, intro_code_alpha)

        if not login_id:
            flash("ログインIDの生成に失敗しました。日付や紹介者NOを確認してください。", "danger")
            return redirect(url_for("register_bp.register"))

        # ✅ 年齢計算
        today = datetime.today()
        age = today.year - birthday_dt.year - ((today.month, today.day) < (birthday_dt.month, birthday_dt.day))

        # ✅ CSVに保存
        file_exists = os.path.exists(USERS_CSV)
        with open(USERS_CSV, "a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow([
                    "ユーザー名", "ふりがな", "生年月日", "年齢", "電話番号",
                    "携帯番号", "メールアドレス", "部署", "職種", "紹介者NO", "ID", "PASS"
                ])
            writer.writerow([
                username, kana, birthday, age, phone, mobile,
                email, department, job_title, intro_code_alpha, login_id, password
            ])

        flash(f"✅ 登録が完了しました！あなたのログインIDは {login_id} です。", "success")
        return redirect(url_for("login_bp.login"))

    return render_template(
        "auth/register.html",
        departments=DEPARTMENTS.values(),
        intro_codes=VALID_INTRO_CODES
    )
