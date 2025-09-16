from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.user import db, User
import random, string

forgot_bp = Blueprint("forgot_bp", __name__, url_prefix="/forgot")

def generate_password(length=8):
    """ランダムな新しいパスワードを生成"""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))

@forgot_bp.route("/", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        mode = request.form.get("mode")  # "id" or "password"
        email = request.form.get("email")

        # 管理者は対象外
        if email == "KING1219":
            flash("⚠️ 管理者は対象外です。運営に直接お問い合わせください。", "error")
            return redirect(url_for("forgot_bp.forgot"))

        user = User.query.filter_by(email=email).first()
        if not user:
            flash("❌ 該当するユーザーが見つかりませんでした。", "error")
            return redirect(url_for("forgot_bp.forgot"))

        if mode == "id":
            # ID照会
            flash(f"✅ あなたのユーザーIDは {user.username} です。", "success")

        elif mode == "password":
            # パスワード再発行
            new_pass = generate_password()
            user.password = new_pass  # 平文保存（本番はハッシュ化推奨）
            db.session.commit()
            flash(f"🔑 新しいパスワードは {new_pass} です。ログイン後に変更してください。", "success")

        return redirect(url_for("forgot_bp.forgot"))

    return render_template("pages/forgot.html")
