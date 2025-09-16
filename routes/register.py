from flask import Blueprint, render_template, request, redirect, url_for, flash
import csv, os

register_bp = Blueprint("register_bp", __name__, url_prefix="/register")

USER_CSV = "research_navi/data/users.csv"

# 職種 → 頭文字2文字のマッピング
JOB_MAP = {
    "営業": "ES",
    "バイヤー": "BY",
    "販売": "SA",
    "物流": "LG",
    "総合": "GN",
    "AI部": "AI"
}

def generate_user_id(job_title, birthdate, referrer_no):
    # 職種コード
    job_code = JOB_MAP.get(job_title, job_title[:2].upper())

    # 誕生日 (YYYY-MM-DD → MMDD)
    birth_mmdd = birthdate.replace("-", "")[4:]

    # 紹介者コード（Kを除外）
    ref_code = referrer_no[1:] if referrer_no.startswith("K") else referrer_no

    # 既存ユーザーを確認して枝番号を決定
    branch_num = 1
    if os.path.exists(USER_CSV):
        with open(USER_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["ID"].startswith(f"{job_code}{birth_mmdd}{ref_code}"):
                    branch_num += 1

    return f"{job_code}{birth_mmdd}{ref_code}{branch_num}"

@register_bp.route("/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        furigana = request.form.get("furigana")
        birthdate = request.form.get("birthdate")
        age = request.form.get("age")
        phone = request.form.get("phone")
        mobile = request.form.get("mobile")
        email = request.form.get("email")
        department = request.form.get("department")
        job_title = request.form.get("job_title")
        referrer_no = request.form.get("referrer_no")
        password = request.form.get("password")

        # ID 自動生成
        user_id = generate_user_id(job_title, birthdate, referrer_no)

        # CSV に保存
        fieldnames = ["ユーザー名","ふりがな","生年月日","年齢","電話番号","携帯番号","メールアドレス","部署","職種","紹介者NO","ID","PASS"]
        file_exists = os.path.exists(USER_CSV)

        with open(USER_CSV, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow({
                "ユーザー名": username,
                "ふりがな": furigana,
                "生年月日": birthdate,
                "年齢": age,
                "電話番号": phone,
                "携帯番号": mobile,
                "メールアドレス": email,
                "部署": department,
                "職種": job_title,
                "紹介者NO": referrer_no,
                "ID": user_id,
                "PASS": password
            })

        flash(f"登録が完了しました！あなたのIDは {user_id} です。", "success")
        return redirect(url_for("login_bp.login"))

    return render_template("pages/register_user.html")
