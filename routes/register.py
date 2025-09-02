from flask import Blueprint, render_template, request, redirect, url_for

register_bp = Blueprint("register_bp", __name__)

@register_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # 登録処理（省略）
        return redirect(url_for("login_bp.login"))
    return render_template("auth/register.html")
