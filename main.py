from flask import Flask, render_template
from routes.login import login_bp
from routes.register import register_bp
from routes.search import search_bp
from routes.ranking import ranking_bp
from routes.static_pages import static_bp

app = Flask(__name__)

# Blueprint 登録
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(search_bp)
app.register_blueprint(ranking_bp)
app.register_blueprint(static_bp)

# エラーハンドラー
@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("errors/500.html"), 500

# ホームルート
@app.route("/")
def home():
    return render_template("pages/home.html")

if __name__ == "__main__":
    app.run(debug=True)

