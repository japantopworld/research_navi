from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from models.user_model import db, User

register_bp = Blueprint("register_bp", __name__, url_prefix="/register")

DEPARTMENTS = {
    "KIN": "鳳陽管理職(その他)",
    "BYR": "バイヤー",
    "KEI": "経理",
    "HAN": "販売員",
    "BUT": "物流",
    "GOT": "合統括"
}

@register_bp.route("/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("username")
        furigana = request.form.get("kana")
        birthdate = request.form.get("birthday")
        tel = request.form.get("tel")
        mobile = request.form.get("mobile")
        email = request.form.get("email")
        department_name = request.form.get("department")
        ref_no = request.form.get("intro_code")
        login_id = request.form.get("login_id")
        password = request.form.get("password")

        # 入力チェック
        errors = []
        if not name:
            errors.append("ユーザー名が未入力です。")
        if not furigana:
            errors.append("ふりがなが未入力です。")
        if not birthdate:
            errors.append("生年月日が未入力です。")
        if not (tel or mobile):
            errors.append("電話番号または携帯番号を入力してください。")
        if not email:
            errors.append("メールアドレスが未入力です。")
        if not login_id:
            errors.append("ログインIDが未入力です。")
        if not password:
            errors.append("パスワードが未入力です。")

        if errors:
            for e in errors:
                flash(e, "danger")
            return redirect(url_for("register_bp.register"))

        try:
            age = datetime.today().year - datetime.strptime(birthdate, "%Y/%m/%d").year
            department_code = next((code for code, name in DEPARTMENTS.items() if name == department_name), "KIN")

            # IDの重複チェック
            existing = User.query.filter_by(login_id=login_id).first()
            if existing:
                flash("このログインIDは既に使われています。", "danger")
                return redirect(url_for("register_bp.register"))

            new_user = User(
                name=name,
                furigana=furigana,
                birthdate=birthdate,
                age=age,
                tel=tel,
                mobile=mobile,
                email=email,
                department=department_name,
                ref_no=ref_no,
                login_id=login_id,
                password=password
            )
            db.session.add(new_user)
            db.session.commit()

            flash(f"登録が完了しました。ログインID: {login_id}", "success")
            session["login_id"] = login_id  # 自動ログイン
            return redirect(url_for("mypage_bp.mypage"))

        except Exception as e:
            flash(f"登録中にエラーが発生しました: {str(e)}", "danger")
            return redirect(url_for("register_bp.register"))

    return render_template("auth/register.html", departments=DEPARTMENTS.values(), intro_codes=["A", "B", "C", "D", "E"])
