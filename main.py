from flask import Flask
import os

app = Flask(__name__)

# Blueprint の読み込み
from routes import search, ranking, dashboard

app.register_blueprint(search.search_bp)
app.register_blueprint(ranking.ranking_bp)
app.register_blueprint(dashboard.dashboard_bp)

# ルート：トップページ（例として）
@app.route("/")
def index():
    return "<h2>ようこそ、リサーチナビへ！</h2><p><a href='/dashboard'>メインダッシュボードへ</a></p>"

# Render向けヘルスチェック（削除してもOKなら消して）
@app.route("/healthz")
def health_check():
    return "ok"

# デプロイ環境対応（Renderで必要）
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
