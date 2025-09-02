from flask import Blueprint, render_template, session

pages_bp = Blueprint("pages_bp", __name__)

@pages_bp.route("/home")
def home():
    return render_template("pages/home.html")
