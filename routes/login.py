from flask import Blueprint, redirect, url_for, session

auth_bp = Blueprint("auth_bp", __name__)

# ✅ /register をテンプレートなしで表示（原因切り分け用）
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    return "<h1>登録ページテスト（テンプレートなし）</h1>"

# ✅ /logout を復活（テンプレート内リンクエラー回避）
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth_bp.login'))

# ✅ /login を仮で定義（ログインページが必要な場合に備えて）
@auth_bp.route('/login')
def login():
    return "<h1>ログインページ（仮）</h1>"
