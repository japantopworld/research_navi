from flask import Flask
from routes.search import search_bp
from routes.home import home_bp
from routes.ranking import ranking_bp
from routes.health_check import health_check_bp
from routes.guide import guide_bp
from routes.login import auth_bp               # ✅ 追加

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Blueprint 登録
app.register_blueprint(home_bp)
app.register_blueprint(search_bp)
app.register_blueprint(ranking_bp)
app.register_blueprint(health_check_bp)
app.register_blueprint(guide_bp)
app.register_blueprint(auth_bp)               # ✅ 追加

# Healthcheck用ルート（Render用）
@app.route('/healthz')
def healthz():
    return "OK"

if __name__ == '__main__':
    app.run(debug=True)
