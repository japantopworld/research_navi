from flask import Blueprint, render_template, request, redirect, url_for, flash

register_bp = Blueprint("register_bp", __name__, url_prefix="/register")

@register_bp.route("/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # 登録ロジック（略）

        flash("登録が完了しました。ログインしてください。", "success")
        return redirect(url_for("login_bp.login"))
    
    return render_template("auth/register.html")
