from flask import Flask, render_template
from models.user import db
from routes.login import login_bp
from routes.register import register_bp
from routes.mypage import mypage_bp
from routes.static_pages import static_pages_bp
from routes.settings import settings_bp
from routes.news import news_bp

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

# ホーム
@app.route("/")
def home():
    return render_template("pages/home.html")

# 健康チェック
@app.route("/healthz")
def healthz():
    return "ok", 200

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # DB初期化
    app.run(host="0.0.0.0", port=10000)
