from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.user import db, User
import re

register_bp = Blueprint("register_bp", __name__, url_prefix="/register")

def generate_user_id(job, birthday, introducer, branch_num=1):
    """職種2文字 + 誕生日MMDD + 紹介者コード + 枝番号 でID作成"""
    job_code = job[:2].upper()
    birthday_code = birthday.replace("-", "")[4:8]  # YYYY-MM-DD → MMDD
    intro_code = introducer[1:] if introducer.startswith("K") else introducer
    return f"{job_code}{birthday_code}{intro_code}{branch_num}"

@register_bp.route("/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # 入力値取得
        username = request.form.get("username")
        furigana = request.form.get("furigana")
        birthday = request.form.get("birthday")
        age = request.form.get("age")
        tel = request.form.get("tel")
        mobile = request.form.get("mobile")
        email = request.form.get("email")
        department = request.form.get("department")
        job = request.form.get("job")
        introducer = request.form.get("introducer")
        password = request.form.get("password")

        # 必須チェック
        if not all([username, furigana, birthday, age, tel, mobile, email, department, job, introducer, password]):
            flash("❌ 全ての項目を入力してください。", "error")
            return redirect(url_for("register_bp.register"))

        # 重複チェック
        if User.query.filter((User.email == email) | (User.tel == tel) | (User.mobile == mobile)).first():
            flash("⚠️ 同じメールまたは電話番号のユーザーが存在します。", "error")
            return redirect(url_for("register_bp.register"))

        # ID自動生成（枝番号の重複確認）
        branch_num = 1
        while True:
            new_id = generate_user_id(job, birthday, introducer, branch_num)
            if not User.query.filter_by(username=new_id).first():
                break
            branch_num += 1

        # ユーザー保存
        new_user = User(
            username=new_id,
            furigana=furigana,
            birthday=birthday,
            age=age,
            tel=tel,
            mobile=mobile,
            email=email,
            department=department,
            job=job,
            introducer=introducer,
            password=password
        )
        db.session.add(new_user)
        db.session.commit()

        flash(f"✅ 登録が完了しました。あなたのIDは {new_id} です。", "success")
        return redirect(url_for("login_bp.login"))

    return render_template("pages/register_user.html")
