from flask import Flask
import os

# アプリ本体
app = Flask(__name__)

# Blueprint登録
from routes import dashboard, search, ranking, guide
app.register_blueprint(dashboard.dashboard_bp)
app.register_blueprint(search.search_bp)
app.register_blueprint(ranking.ranking_bp)
app.register_blueprint(guide.guide_bp)

# Health check（Render用）
@app.route("/healthz")
def health_check():
    return "ok"

# waitress起動
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
