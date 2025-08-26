from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models.user_model import db  # SQLAlchemyインスタンスをインポート
import os

# ルーティング
from routes.login import login_bp
from routes.register import register_bp
from routes.home import home_bp
from routes.mypage import mypage_bp
from routes.logout import logout_bp

app = Flask(__name__)
app.secret_key = "your_secret_key"

# ✅ Render用：PostgreSQL 環境変数から読み取る
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# SQLAlchemyにFlaskアプリを登録
db.init_app(app)

# Blueprint登録
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(home_bp)
app.register_blueprint(mypage_bp)
app.register_blueprint(logout_bp)

# Health check（Render対策）
@app.route("/healthz")
def healthz():
    return "ok", 200

# アプリ起動
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # テーブル作成（初回のみ有効）
    app.run(debug=True)
