from flask import Blueprint

# ✅ Blueprint を先に定義する
auth_bp = Blueprint("auth_bp", __name__)

# ✅ ここからルート定義
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    return "<h1>登録ページテスト（テンプレートなし）</h1>"
