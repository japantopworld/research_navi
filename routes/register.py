import csv
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash

register_bp = Blueprint("register_bp", __name__, url_prefix="/register")

CSV_FILE = "data/users.csv"

# ID自動生成ロジック
def generate_user_id(job, birth, ref_code):
    job_code = job[:2].upper()  # 職種の頭2文字
    birth_code = birth.replace("-", "")[4:8]  # MMDD 抜き出し
    ref_code_clean = ref_code[1:] if ref_code.startswith("K") else ref_code
    base_id = f"{job_code}{birth_code}{ref_code_clean}"

    # 重複チェック（枝番号をつける）
    existing_ids = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_ids.append(row["ID"])

    new_id = base_id
    i = 1
    while new_id in existing_ids:
        new_id = f"{base_id}{i}"
        i += 1

    return new_id


@register_bp.route("/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        furigana = request.form.get("furigana")
        birth = request.form.get("birth")
        age = request.form.get("age")
        tel = request.form.get("tel")
        mobile = request.form.get("mobile")
        email = request.form.get("email")
        dept = request.form.get("dept")
        job = request.form.get("job")
        ref_code = request.form.get("ref_code")
        password = request.form.get("password")

        # 必須チェック
        if not all([username, furigana, birth, age, email, dept, job, ref_code, password]):
            flash("⚠️ 未入力の必須項目があります。", "error")
            return redirect(url_for("register_bp.register"))
        if not (tel or mobile):
            flash("⚠️ 電話番号または携帯番号のどちらかは必須です。", "error")
            return redirect(url_for("register_bp.register"))
        if len(password) < 6:
            flash("⚠️ パスワードは6文字以上で入力してください。", "error")
            return redirect(url_for("register_bp.register"))

        # メール重複チェック
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["メールアドレス"] == email:
                        flash("⚠️ このメールアドレスは既に登録されています。", "error")
                        return redirect(url_for("register_bp.register"))

        # ID自動生成
        user_id = generate_user_id(job, birth, ref_code)

        # CSVに保存
        file_exists = os.path.exists(CSV_FILE)
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            fieldnames = [
                "ユーザー名", "ふりがな", "生年月日", "年齢",
                "電話番号", "携帯番号", "メールアドレス", "部署", "職種",
                "紹介者NO", "ID", "PASS"
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow({
                "ユーザー名": username,
                "ふりがな": furigana,
                "生年月日": birth,
                "年齢": age,
                "電話番号": tel,
                "携帯番号": mobile,
                "メールアドレス": email,
                "部署": dept,
                "職種": job,
                "紹介者NO": ref_code,
                "ID": user_id,
                "PASS": password
            })

        # 成功画面へ
        return render_template("pages/register_success.html", user_id=user_id)

    return render_template("pages/register_user.html")
