from flask import Flask, render_template
from routes.login import auth_bp
from routes.news import news_bp
from routes.static_pages import static_pages_bp  # ← サポート/ガイド/規約/FAQ/お問い合わせ

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Blueprint 登録
app.register_blueprint(auth_bp)
app.register_blueprint(news_bp)
app.register_blueprint(static_pages_bp)

# ホーム
@app.route("/")
def home():
    return render_template("pages/home.html")

# 健康チェック（Render用）
@app.route("/healthz")
def healthz():
    return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
