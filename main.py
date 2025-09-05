from flask import Flask
from routes.login import login_bp
from routes.register import register_bp
from routes.home import home_bp
from routes.ranking import ranking_bp
from routes.guide import guide_bp
from routes.admin import admin_bp
from routes.health_check import health_bp  # 必ず追加！

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Blueprint登録
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(home_bp)
app.register_blueprint(ranking_bp)
app.register_blueprint(guide_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(health_bp)  # ✅ /healthzエンドポイントを追加

# 明示的な /healthz 定義（Render向け）
@app.route("/healthz")
def health_check_direct():
    return "OK", 200

# ローカル起動用（本番では使われない）
if __name__ == '__main__':
    app.run(debug=True)
