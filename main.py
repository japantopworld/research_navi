from flask import Flask, render_template, session, redirect, url_for
from routes.login import login_bp
from routes.register import register_bp
from routes.search import search_bp
from routes.ranking import ranking_bp
from routes.static_pages import static_pages_bp

app = Flask(__name__)
app.secret_key = "your-secret-key"  # セキュリティ上、実運用では安全なキーに変更してください

# Blueprint 登録（すべて明示）
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(search_bp)
app.register_blueprint(ranking_bp)
app.register_blueprint(static_pages_bp)

# ホーム画面
@app.route("/")
def home():
    if "user" not in session:
        return redirect(url_for("login.login"))
    return render_template("pages/home.html")

# エラーページ
@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("errors/500.html"), 500

# Render用（health check endpoint）
@app.route("/healthz")
def health_check():
    return "OK"

if __name__ == "__main__":
    app.run(debug=True)
