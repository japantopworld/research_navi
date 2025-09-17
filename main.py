# research_navi/main.py
from flask import Flask, render_template, session, redirect, url_for
from models.user import db

# 認証・共通系
from routes.login import login_bp
from routes.register import register_bp
from routes.mypage import mypage_bp
from routes.static_pages import static_pages_bp
from routes.settings import settings_bp
from routes.news import news_bp

# 部署別 Blueprints
from routes.general_admin import general_admin_bp
from routes.buyer import buyer_bp
from routes.sales import sales_bp
from routes.logistics import logistics_bp
from routes.ai_finance import ai_finance_bp

app = Flask(__name__)
app.secret_key = "your_secret_key"

# DB 設定（SQLite）
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data/users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Blueprint 登録
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(mypage_bp)
app.register_blueprint(static_pages_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(news_bp)

# 部署別 Blueprint 登録
app.register_blueprint(general_admin_bp)
app.register_blueprint(buyer_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(logistics_bp)
app.register_blueprint(ai_finance_bp)

# ホーム
@app.route("/")
def home():
    return render_template("pages/home.html")

# マイページ（ログイン必須）
@app.route("/mypage_redirect")
def mypage_redirect():
    if "user_id" not in session:
        return redirect(url_for("login_bp.login"))
    return redirect(url_for("mypage_bp.mypage"))

# 健康チェック
@app.route("/healthz")
def healthz():
    return "ok", 200

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # DB初期化
    app.run(host="0.0.0.0", port=10000)
