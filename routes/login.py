from flask import Blueprint, render_template, request, redirect, session, url_for
import csv
import os

login_bp = Blueprint('login', __name__, url_prefix='/login')

# CSVファイルからユーザー読み込み
def load_users():
    users = {}
    if os.path.exists('data/users.csv'):
        with open('data/users.csv', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    users[row[0]] = row[1]
    return users

@login_bp.route('/', methods=['GET', 'POST'])
def login():
    error = None
    users = load_users()

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in users and users[username] == password:
            session['user'] = username
            return redirect('/')
        else:
            error = "IDまたはパスワードが違います"

    return render_template('pages/login.html', error=error)
