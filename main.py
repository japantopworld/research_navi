from flask import Flask
import os

app = Flask(__name__)

# Blueprintの読み込み（routes フォルダの .py に合わせて）
from routes import search, ranking, dashboard

app.register_blueprint(search.search_bp)
app.register_blueprint(ranking.ranking_bp)
app.register_blueprint(dashboard.dashboard_bp)

# Health Check（Renderが起動確認に使うURL）
@app.route("/healthz")
def health_check():
    return "ok"

# waitressで起動（Render対応）
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
