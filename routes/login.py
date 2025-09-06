# routes/login.py

from flask import Blueprint, render_template, request, redirect, url_for, session
import csv
import os

auth_bp = Blueprint("auth_bp", __name__)

# 管理者アカウント
ADMIN_ID = "KING1192"
ADMIN_PASS = "11922960"

USERS_CSV_PATH = "data/users.csv"  # 修正済み：data/配下を想定

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_id = request.form['id']
        password = request.form['password']

        if login_id == ADMIN_ID and password == ADMIN_PASS:
            session['user_id'] = login_id
            session['role'] = 'admin'
            return redirect(url_for('home_bp.home'))

        if os.path.exists(USERS_CSV_PATH):
            with open(USERS_CSV_PATH, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row['ID'] == login_id and row['PASS'] == password:
                        session['user_id'] = login_id
                        session['role'] = 'user'
                        return redirect(url_for('home_bp.home'))

        return render_template('auth/login.html', error='IDまたはパスワードが違います')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth_bp.login'))
