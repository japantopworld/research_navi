from flask import Blueprint, render_template, request, redirect, url_for, flash
import csv, os

register_bp = Blueprint("register_bp", __name__, url_prefix="/register")

# CSVファイルのパス
CSV_FILE = os.path.join("data", "users.csv")

@register_bp.route("/", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        furigana = request.form.get("furigana", "").strip()
        birthdate = request.form.get("birthdate", "").strip()
        age = request.form.get("age", "").strip()
        phone = request.form.get("phone", "").strip()
        mobile = request.form.get("mobile", "").strip()
        email = request.form.get("email", "").strip()
        department = request.form.get("department", "").strip()
        role = request.form.get("role", "").strip()
        ref_code = request.form.get("ref_code", "").strip()
        password = request.form.get("password", "").strip()

        # ✅ サーバー側バリデーション
        if not birthdate:
            error = "生年月日は必須です。"
        elif not username or not furigana or not age or not email or not department or not role:
            error = "必須項目が未入力です。"
        elif not phone and not mobile:
            error = "電話番号または携帯番号のどちらかは必須です。"
        elif len(password) < 6:
            error = "パスワードは6文字以上で入力してください。"

        if error:
            return render_template("pages/register_user.html", error=error)

        # ✅ ID自動生成ロジック
        # 職種の頭文字2つ + 誕生日(MMDD) + 紹介者コード
        birth_mmdd = birthdate.replace("-", "")[4:8]  # YYYY-MM-DD → MMDD
        role_prefix = role[:2].upper()
        ref = ref_code[1:] if ref_code.startswith("K") else ref_code
        user_id = f"{role_prefix}{birth_mmdd}{ref}"

        # ✅ CSVに保存
        new_user = [
            username, furigana, birthdate, age,
            phone, mobile, email, department, role,
            ref_code, user_id, password
        ]
        os.makedirs("data", exist_ok=True)
        write_header = not os.path.exists(CSV_FILE)
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(["ユーザー名","ふりがな","生年月日","年齢",
                                 "電話番号","携帯番号","メールアドレス",
                                 "部署","職種","紹介者NO","ID","PASS"])
            writer.writerow(new_user)

        flash(f"登録完了！ID: {user_id} を発行しました。", "success")
        return redirect(url_for("login_bp.login"))

    return render_template("pages/register_user.html", error=error)
