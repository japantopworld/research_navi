# main.py

from flask import Flask
from routes.search import search_bp
from routes.home import home_bp
from routes.health_check import health_check_bp  # 他のBlueprintも必要に応じて追加

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Blueprint 登録
app.register_blueprint(home_bp)
app.register_blueprint(search_bp)
app.register_blueprint(health_check_bp)  # 他にも必要ならここで登録

# Healthcheck用ルート（Render用）
@app.route('/healthz')
def healthz():
    return "OK"

if __name__ == '__main__':
    app.run(debug=True)
