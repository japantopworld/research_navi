from flask import Flask, render_template, redirect, url_for, session
from routes.login import login_bp
from routes.register import register_bp
from routes.mypage import mypage_bp

app = Flask(__name__)
app.secret_key = "your_secret_key"  # セキュリティのため必須！

# Blueprint 登録
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(mypage_bp)

# ✅ トップページ（誰でもアクセス可能）
@app.route("/")
def home():
    return render_template("pages/home.html")

# ✅ /healthz（Render用のヘルスチェック）
@app.route("/healthz")
def health_check():
    return "ok", 200

# ✅ 404 エラーハンドリング
@app.errorhandler(404)
def not_found(e):
    return render_template("errors/404.html"), 404

# ✅ 500 エラーハンドリング
@app.errorhandler(500)
def internal_error(e):
    return render_template("errors/500.html"), 500

if __name__ == "__main__":
    app.run(debug=True)
