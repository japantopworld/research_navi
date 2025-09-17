# research_navi/routes/general_admin.py
from flask import Blueprint, render_template, session, redirect, url_for

# Blueprint の名前は "general_admin_bp"
general_admin_bp = Blueprint("general_admin_bp", __name__, url_prefix="/general_admin")

@general_admin_bp.route("/")
def general_admin():
    if "user_id" not in session:
        return redirect(url_for("login_bp.login"))
    return render_template("pages/general_admin.html")
