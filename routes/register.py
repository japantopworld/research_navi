from flask import Blueprint, render_template, request, redirect, url_for, flash
import csv, os

register_bp = Blueprint("register_bp", __name__, url_prefix="/register")

DATA_FILE = "data/users.csv"

@register_bp.route("/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        furigana = request.form.get("furigana")
        birth = request.form.get("birth")  # YYYY-MM-DD
        age = request.form.get("age")
        tel = request.form.get("tel")
        mobile = request.form.get("mobile")
        email = request.form.get("email")
        dept = request.form.get("dept")
        job = request.form.get("job")
        ref_code = request.form.get("ref_code")  # KA～KE
        password = request.form.get("password")

        # 必須チェック
        if not all([username, furigana, birth, age, email, dept, job, ref_code, password]):
            flash("必須項目が未入力です ❌", "danger")
            return redirect(url_for("register_bp.register"))
        if not tel and not mobile:
            flash("電話番号または携帯番号のいずれかは必須です ❌", "danger")
            return redirect(url_for("register_bp.register"))
        if len(password) < 6:
            flash("パスワードは6文字以上で入力してください ❌", "danger")
            return redirect(url_for("register_bp.register"))

        # 誕生日のMMDDを抽出
        birth_mmdd = birth.replace("-", "")[4:8]  # YYYYMMDD → MMDD

        # 紹介者コード（Kを外す）
        if ref_code.startswith("K"):
            ref_code_clean = ref_code[1:]
        else:
            ref_code_clean = ref_code

        # ID生成: 職種頭2 + 誕生日MMDD + 紹介者コード
        user_id = job[:2].upper() + birth_mmdd + ref_code_clean

        # CSVに保存
        os.makedirs("data", exist_ok=True)
        file_exists = os.path.isfile(DATA_FILE)
        with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["ユーザー名", "ふりがな", "生年月日", "年齢", "電話番号", "携帯番号",
                            "メールアドレス", "部署", "職種", "紹介者NO", "ID", "PASS"]
            )
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

        # 完了画面へ
        return render_template("pages/register_success.html",
                               user_id=user_id,
                               username=username)

    return render_template("pages/register_user.html")
