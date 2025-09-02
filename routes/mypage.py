from flask import Blueprint, render_template, session, redirect, url_for

mypage_bp = Blueprint("mypage_bp", __name__)

@mypage_bp.route("/mypage")
def mypage():
    if 'user_id' not in session:
        return redirect(url_for('login_bp.login'))
    return render_template("pages/mypage.html")
