from flask import Flask, render_template, session
from routes.login import auth_bp  # ✅ login Blueprint を読み込み
# from routes.news import news_bp  # ← まだ routes/news.py が無いのでコメントアウト

app = Flask(__name__)
app.secret_key = "your_secret_key"  # セッション用

# ==============================
# Blueprint 登録
# ==============================
app.register_blueprint(auth_bp)
# app.register_blueprint(news_bp)   # ← news 機能を作ったら有効化


# ==============================
# ルート定義
# ==============================

# ホーム画面
@app.route("/")
def home():
    return render_template("pages/home.html")


# 利用規約
@app.route("/terms")
def terms():
    return render_template("policy/terms.html")


# プライバシーポリシー
@app.route("/privacy")
def privacy():
    return render_template("policy/privacy.html")


# 使い方ガイド
@app.route("/guide")
def guide():
    return render_template("pages/guide.html")


# サービス一覧
@app.route("/services")
def services():
    return render_template("pages/services.html")


# お問い合わせ
@app.route("/support")
def support():
    return render_template("pages/support.html")


# 違反通報フォーム
@app.route("/report")
def report():
    return render_template("pages/report.html")


# マイページ（ログイン必須）
@app.route("/mypage/<user_id>")
def mypage(user_id):
    if not session.get("logged_in"):
        return render_template("pages/login.html", error="ログインしてください")
    return render_template("pages/mypage.html", user_id=user_id)


# 各種設定
@app.route("/settings")
def settings():
    if not session.get("logged_in"):
        return render_template("pages/login.html", error="ログインしてください")
    return render_template("pages/settings.html")


# ==============================
# Health Check
# ==============================
@app.route("/healthz")
def healthz():
    return "ok", 200


# ==============================
# 実行
# ==============================
if __name__ == "__main__":
    app.run(debug=True)
