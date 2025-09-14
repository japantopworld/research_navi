import os
from flask import Flask, render_template

# -----------------------------
# Flask app
# -----------------------------
app = Flask(__name__)
app.secret_key = "change-me"

# -----------------------------
# Blueprint 読み込み
# -----------------------------
from routes.login import login_bp
from routes.register import register_bp
from routes.news import news_bp

# Blueprint 登録
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(news_bp)

# -----------------------------
# トップページ
# -----------------------------
@app.route("/")
def home():
    return render_template("pages/home.html")

# -----------------------------
# Render 用ヘルスチェック
# -----------------------------
@app.route("/healthz")
def healthz():
    return "OK", 200

# -----------------------------
# ローカル実行用
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
