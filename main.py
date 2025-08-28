from flask import Flask, render_template, redirect, url_for, session
from routes.login import login_bp
from routes.logout import logout_bp
from routes.register import register_bp
from routes.home import home_bp
from routes.policy import policy_bp  # ✅ 利用規約用

import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "default_secret_key")

# Blueprint 登録
app.register_blueprint(login_bp)
app.register_blueprint(logout_bp)
app.register_blueprint(register_bp)
app.register_blueprint(home_bp)
app.register_blueprint(policy_bp)  # ✅ 利用規約のルートを有効化

# ルートはホームにリダイレクト
@app.route("/")
def index():
    return redirect(url_for("home_bp.home"))

# ✅ ヘルスチェック用
@app.route("/healthz")
def health_check():
    return "OK"

# エラーハンドラ
@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("errors/500.html"), 500

if __name__ == "__main__":
    app.run(debug=True)
