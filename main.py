from flask import Flask, render_template, redirect, url_for, session
from routes.login import login_bp
from routes.register import register_bp
from routes.buyer import buyer_bp
from routes.sales import sales_bp
from routes.logistics import logistics_bp
from routes.general import general_bp
from routes.news import news_bp
from routes.accounting import accounting_bp   # ← 経理部を追加

app = Flask(__name__)
app.secret_key = "your-secret-key"  # セッション用の秘密鍵

# ===== Blueprint登録 =====
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(buyer_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(logistics_bp)
app.register_blueprint(general_bp)
app.register_blueprint(news_bp)
app.register_blueprint(accounting_bp)   # ← 経理部を登録

# ===== ルート =====
@app.route("/")
def home():
    # 未ログイン時はログイン画面へリダイレクト
    if "user_id" not in session:
        return redirect(url_for("login_bp.login"))
    return render_template("pages/home.html")

@app.route("/mypage")
def mypage():
    if "user_id" not in session:
        return redirect(url_for("login_bp.login"))
    display_name = session.get("display_name", "ゲスト")
    return render_template("pages/mypage.html", display_name=display_name)

# Healthチェック用
@app.route("/healthz")
def healthz():
    return "ok", 200

# ===== エラーハンドラ =====
@app.errorhandler(404)
def not_found(e):
    return render_template("errors/404.html"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("errors/500.html"), 500

# ===== エントリーポイント =====
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
