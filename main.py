import os
from flask import Flask, render_template
from routes.register import register_bp
from routes.search import search_bp
from routes.ranking import ranking_bp
from routes.static_pages import static_pages_bp

app = Flask(__name__)

# Blueprintの登録
app.register_blueprint(register_bp)
app.register_blueprint(search_bp)
app.register_blueprint(ranking_bp)
app.register_blueprint(static_pages_bp)

# ホームページ表示
@app.route("/")
def home():
    return render_template("pages/dashboard.html")

# 404 エラーハンドラー
@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404

# 500 エラーハンドラー
@app.errorhandler(500)
def internal_error(error):
    return render_template("errors/500.html"), 500

# アプリ起動
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
