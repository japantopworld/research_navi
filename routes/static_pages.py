# routes/static_pages.py

from flask import Blueprint, render_template

static_pages_bp = Blueprint("static_pages", __name__)

@static_pages_bp.route("/terms")
def terms():
    return render_template("pages/terms.html")

@static_pages_bp.route("/privacy")
def privacy():
    return render_template("pages/privacy.html")

@static_pages_bp.route("/guide")
def guide():
    return render_template("pages/guide.html")
