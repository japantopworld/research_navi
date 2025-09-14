from flask import Flask, render_template, session
from routes.login import auth_bp   # ← login Blueprint を読み込み

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Blueprint 登録
app.register_blueprint(auth_bp)

# -----------------------------
# ホーム
# -----------------------------
@app.route("/")
def home():
    if not session.get("logged_in"):
        return render_template("pages/login.html")  # 未ログインならログインページへ
    return render_template("pages/home.html")


# -----------------------------
# 健康チェック（Render用）
# -----------------------------
@app.route("/healthz")
def healthz():
    return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
