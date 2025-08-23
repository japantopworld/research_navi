from flask import Flask
from routes.login import login_bp
from routes.register import register_bp
from routes.home import home_bp

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Blueprint 登録
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(home_bp)

# ✅ ヘルスチェック対応（Render用）
@app.route("/healthz")
def health_check():
    return "OK"

# ✅ 404 ページ対応
@app.errorhandler(404)
def page_not_found(e):
    return "ページが見つかりませんでした（404）", 404

if __name__ == "__main__":
    app.run(debug=True)
