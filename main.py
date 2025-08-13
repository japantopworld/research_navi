# main.py
import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

def normalize_db_url(raw: str | None) -> str:
    # RenderのURLが postgres:// / postgresql:// だけの場合はドライバを補う
    if not raw:
        # 環境変数未設定時はローカルSQLiteにフォールバック
        return "sqlite:///data/app.db"
    if raw.startswith("postgres://"):
        return "postgresql+psycopg://" + raw[len("postgres://"):]
    if raw.startswith("postgresql://") and "+psycopg" not in raw and "+psycopg2" not in raw:
        # psycopg(3) を使う前提。方法Bでpsycopg2を入れる場合はこの行はそのままでも動きます。
        return "postgresql+psycopg://" + raw[len("postgresql://"):]
    return raw

app = Flask(__name__)

db_url = normalize_db_url(os.getenv("DATABASE_URL"))
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# --- 以降は既存のルーティング（例） ---
@app.route("/")
def home():
    return render_template("pages/home.html")

@app.route("/search")
def search():
    return render_template("pages/search.html")

@app.route("/profit")
def profit():
    return render_template("pages/profit.html")

@app.route("/history")
def history():
    return render_template("pages/history.html")

@app.route("/ranking")
def ranking():
    return render_template("pages/ranking.html")

@app.route("/notifications")
def notifications():
    return render_template("pages/notifications.html")

@app.route("/ocr")
def ocr():
    return render_template("pages/ocr.html")

@app.route("/suppliers")
def suppliers():
    return render_template("pages/suppliers.html")

@app.route("/setting")
def setting():
    return render_template("pages/setting.html")

@app.errorhandler(404)
def not_found(e):
    return render_template("errors/404.html"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("errors/500.html"), 500

if __name__ == "__main__":
    # ローカル実行用
    app.run(debug=True)
