from flask import Blueprint, redirect, url_for, session

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    return "<h1>登録ページテスト（テンプレートなし）</h1>"

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth_bp.login'))

@auth_bp.route('/login')
def login():
    return "<h1>ログインページ（仮）</h1>"
