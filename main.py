from flask import Flask
from routes.home import home_bp
from routes.search import search_bp
from routes.ranking import ranking_bp
from routes.health_check import health_check_bp
from routes.login import auth_bp
from routes.guide import guide_bp  # ✅ 追加

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Blueprint 登録
app.register_blueprint(home_bp)
app.register_blueprint(search_bp)
app.register_blueprint(ranking_bp)
app.register_blueprint(health_check_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(guide_bp)  # ✅ 追加

# Render 用
@app.route('/healthz')
def healthz():
    return "OK"

# ✅ テストルート：Flaskが動いているか確認
@app.route('/test-register')
def test_register():
    return "Register route is working"

# ✅ ルート一覧表示：Flaskが認識しているURLを確認
@app.route('/routes')
def show_routes():
    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = f"{rule.endpoint:30s} {methods:20s} {rule.rule}"
        output.append(line)
    return "<pre>" + "\n".join(output) + "</pre>"

# ✅ 一時的な直接ルート：Blueprintを使わずに /register を処理
@app.route('/register')
def test_direct_register():
    return "Register route is working (direct)"

if __name__ == '__main__':
    app.run(debug=True)
