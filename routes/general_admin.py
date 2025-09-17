# research_navi/routes/general_admin.py
from flask import Blueprint, render_template, session, redirect, url_for

general_admin_bp = Blueprint("general_admin_bp", __name__)

@general_admin_bp.route("/admin/general")
def general_admin():
    if "user_id" not in session:
        return redirect(url_for("login_bp.login"))
    return render_template("pages/general_admin.html")

