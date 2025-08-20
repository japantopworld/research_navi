from flask import Flask
import os

app = Flask(__name__)

# Blueprint 読み込み
from routes import dashboard, search, ranking

app.register_blueprint(dashboard.dashboard_bp)
app.register_blueprint(search.search_bp)
app.register_blueprint(ranking.ranking_bp)

# Render用Health Check
@app.route("/healthz")
def health_check():
    return "ok"

# waitress起動（Render対応）
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
