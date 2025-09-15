from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.user import User, db
from utils.user_sync import save_user_to_csv, sync_csv_to_db

register_bp = Blueprint("register_bp", __name__, url_prefix="/register")

@register_bp.route("/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")

        # すでに登録されているかチェック
        if User.query.filter_by(username=username).first():
            flash("⚠️ このユーザー名は既に登録されています。", "danger")
            return redirect(url_for("register_bp.register"))

        # 新規ユーザー作成
        new_user = User(username=username, password=password, email=email)
        db.session.add(new_user)
        db.session.commit()

        # CSV にも保存
        save_user_to_csv(new_user)

        flash("✅ 登録が完了しました。ログインしてください。", "success")
        return redirect(url_for("login_bp.login"))

    return render_template("pages/register_user.html")
