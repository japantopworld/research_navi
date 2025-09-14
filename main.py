import os, csv
from flask import Flask, render_template, session
from routes.login import auth_bp   # ← login用Blueprintだけ残す
# from routes.news import news_bp  # ← 今は未実装なので削除

app = Flask(__name__)
app.secret_key = "change-me"

# -----------------------------
# Blueprint 登録
# -----------------------------
app.register_blueprint(auth_bp)
# app.register_blueprint(news_bp)  # ← コメントアウト

# -----------------------------
# ルート
# -----------------------------
@app.route("/")
def home():
    return render_template("pages/home.html")

# -----------------------------
# /healthz (Render用の死活監視)
# -----------------------------
@app.route("/healthz")
def healthz():
    return "ok", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
