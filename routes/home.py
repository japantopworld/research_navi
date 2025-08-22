from flask import Blueprint, render_template, session

home_bp = Blueprint("home_bp", __name__)

@home_bp.route("/home")
def home():
    user_name = session.get("user_name", "ゲスト")
    return render_template("pages/home.html", user_name=user_name)
