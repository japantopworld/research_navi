from flask import Flask
from routes.login import login_bp
from routes.register import register_bp
from routes.home import home_bp
from flask_sqlalchemy import SQLAlchemy

# データベース設定
from models.user_model import db

app = Flask(__name__)
app.secret_key = "your_secret_key"

# SQLite DBファイル（ローカル）保存先
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data/users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# データベース初期化
db.init_app(app)

# Blueprint登録
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(home_bp)

# Health check（Render対応用）
@app.route("/healthz")
def healthz():
    return "ok", 200

# アプリ起動
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # ← テーブル自動生成
    app.run(debug=True)
