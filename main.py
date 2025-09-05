from flask import Flask
from routes.login import login_bp
from routes.register import register_bp
from routes.home import home_bp
from routes.mypage import mypage_bp
from routes.health_check import health_check_bp  # ← /healthz 対応

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # セッション用

# Blueprint登録
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(home_bp)
app.register_blueprint(mypage_bp)
app.register_blueprint(health_check_bp)  # ← ヘルスチェック用

# ルートページ（必要なら）
@app.route("/")
def index():
    return "🌐 リサーチナビへようこそ！（トップページ）"

if __name__ == "__main__":
    app.run(debug=True)
