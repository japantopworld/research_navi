from flask import Flask
import os

# Flaskアプリ初期化
app = Flask(__name__)

# Blueprint読み込み
from routes import dashboard, search, ranking, home  # ← homeも追加する

app.register_blueprint(home.home_bp)         # トップページ
app.register_blueprint(dashboard.dashboard_bp)
app.register_blueprint(search.search_bp)
app.register_blueprint(ranking.ranking_bp)

# Health Check（Render用）
@app.route("/healthz")
def health_check():
    return "ok"

# 本番用起動（waitress）
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
