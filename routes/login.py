# routes/login.py
from flask import Blueprint, render_template, request, redirect, url_for

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'pass':
            return redirect(url_for('dashboard.dashboard'))
        else:
            return "ログイン失敗", 401
    return render_template("pages/login.html")
