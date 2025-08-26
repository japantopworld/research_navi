from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models.user_model import db

# Blueprintルート
from routes.login import login_bp
from routes.register import register_bp
from routes.home import home_bp
from routes.mypage import mypage_bp
from routes.logout import logout_bp

app = Flask(__name__)
app.secret_key = "your_secret_key"

# 本番用（PostgreSQL）
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg://<ユーザー名>:<パスワード>@<ホスト名>:5432/<DB名>"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Blueprint 登録
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(home_bp)
app.register_blueprint(mypage_bp)
app.register_blueprint(logout_bp)

# ヘルスチェック
@app.route("/healthz")
def healthz():
    return "ok", 200

# アプリ起動
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
