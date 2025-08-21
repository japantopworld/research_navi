from flask import Flask, render_template, session
from routes.login import login_bp
from routes.register import register_bp
from routes.search import search_bp
from routes.ranking import ranking_bp
from routes.static_pages import static_pages_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Blueprint 登録
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(search_bp)
app.register_blueprint(ranking_bp)
app.register_blueprint(static_pages_bp)

# エラーハンドラー
@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("errors/500.html"), 500

# ✅ ホームルート（ログイン前後で切り替え）
@app.route("/")
def home():
    if 'user_id' in session:
        return render_template("pages/home.html")  # ログイン済み
    else:
        return render_template("pages/welcome.html")  # ログイン前

# ✅ Render 用ヘルスチェック
@app.route("/healthz")
def health_check():
    return "OK", 200

# ✅ PORT指定でRender対応
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
