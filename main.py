from flask import Flask, render_template, session
from routes.login import login_bp
from routes.mypage import mypage_bp
from routes.static_pages import static_pages_bp
from routes.settings import settings_bp
from routes.news import news_bp

app = Flask(__name__)
app.secret_key = "your-secret-key"  # 本番は環境変数で設定推奨

# 🔹 Blueprint登録
app.register_blueprint(login_bp)
app.register_blueprint(mypage_bp)
app.register_blueprint(static_pages_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(news_bp)

# -------------------------
# ホーム画面
# -------------------------
@app.route("/")
def home():
    return render_template("pages/home.html")

# -------------------------
# Render用のヘルスチェック
# -------------------------
@app.route("/healthz")
def healthz():
    return "ok", 200


# -------------------------
# 実行
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
