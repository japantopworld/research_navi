# routes/logout.py

from flask import Blueprint, redirect, url_for, session, flash

logout_bp = Blueprint("logout_bp", __name__)

@logout_bp.route("/logout")
def logout():
    session.clear()
    flash("ログアウトしました。", "info")
    return redirect(url_for("home_bp.home"))
