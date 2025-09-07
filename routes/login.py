from flask import Blueprint, redirect, url_for, session

# ✅ Blueprint を先に定義
auth_bp = Blueprint("auth_bp", __name__)

# ✅ /register（テンプレートなしで表示）
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    return "<h1>登録ページテスト（テンプレートなし）</h1>"

# ✅ /logout（テンプレート内リンク対策）
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth_bp.login'))

# ✅ /login（仮のログインページ）
@auth_bp.route('/login')
def login():
    return "<h1>ログインページ（仮）</h1>"
