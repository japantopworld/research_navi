from flask import Blueprint, redirect, url_for, session

# ✅ Blueprint を先に定義
auth_bp = Blueprint("auth_bp", __name__)

# ✅ /login（仮のログインページ）
@auth_bp.route('/login')
def login():
    return "<h1>ログインページ（仮）</h1>"

# ✅ /logout（セッション削除）
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth_bp.login'))

# ✅ /register（テンプレートなしで表示）
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    return "<h1>登録ページテスト（テンプレートなし）</h1>"
    
