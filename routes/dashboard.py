from flask import Blueprint, render_template
import datetime

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
    current_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M")
    return render_template("pages/dashboard.html", current_time=current_time)
