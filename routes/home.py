from flask import Blueprint, render_template, session, redirect, url_for

home_bp = Blueprint("home_bp", __name__)

@home_bp.route("/")
def home():
    if "user_id" in session:
        user_name = session.get("user_name", "ゲスト")
        return render_template("pages/home.html", user_name=user_name)
    else:
        return render_template("pages/welcome.html")
