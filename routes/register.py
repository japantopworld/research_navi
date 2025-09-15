from flask import Blueprint, render_template, request, redirect, url_for, flash

# Blueprint を定義
register_bp = Blueprint("register_bp", __name__, url_prefix="/register")

@register_bp.route("/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # 🚨 仮の登録ロジック（今はDB未接続なのでダミー）
        if not username or not password:
            flash("ユーザー名とパスワードを入力してください。", "danger")
            return redirect(url_for("register_bp.register"))

        # 本番では users.csv や DB に保存する処理をここに追加
        flash(f"ユーザー {username} を登録しました。ログインしてください。", "success")
        return redirect(url_for("login_bp.login"))

    # GET の場合 → 登録フォームを表示
    return render_template("pages/register.html")
