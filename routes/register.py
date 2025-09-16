from flask import Blueprint, render_template, request, redirect, url_for, flash
import datetime

register_bp = Blueprint("register_bp", __name__, url_prefix="/register")

# 仮のユーザーデータ保存リスト（本番はDB利用を想定）
users = []

def generate_user_id(job_title, birthdate, referrer_no):
    """
    職種2文字 + 誕生日MMDD + 紹介者コード(先頭Kを除外) + 枝番号
    """
    # 職種 → 先頭2文字
    job_code = job_title[:2].upper()

    # 誕生日 → MMDD
    try:
        date_obj = datetime.datetime.strptime(birthdate, "%Y-%m-%d")
        birth_code = date_obj.strftime("%m%d")
    except Exception:
        birth_code = "0000"

    # 紹介者コード処理（KA, KB → A, B）
    ref_code = ""
    branch_num = ""
    if referrer_no:
        if referrer_no.startswith("K") and len(referrer_no) >= 2:
            ref_code = referrer_no[1]  # 先頭のKを除去して1文字取得
            branch_num = referrer_no[2:] if len(referrer_no) > 2 else ""
        else:
            ref_code = referrer_no  # Kがない場合そのまま

    return f"{job_code}{birth_code}{ref_code}{branch_num}"

@register_bp.route("/", methods=["GET", "POST"])
def register():
    generated_id = None
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

        # ID自動生成
        generated_id = generate_user_id(job_title, birthdate, referrer_no)

        # 仮保存（本番はDBに保存）
        users.append({
            "ID": generated_id,
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
            "PASS": password
        })

        flash(f"登録完了 🎉 あなたのIDは {generated_id} です。", "success")

        # IDを登録画面に渡して表示
        return render_template("pages/register_user.html", generated_id=generated_id)

    return render_template("pages/register_user.html", generated_id=generated_id)
