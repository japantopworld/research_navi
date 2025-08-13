import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy

# ------------ Flask -------------
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "rn-dev-secret")

# ------------ DB (Postgres / SQLite 自動判定) -------------
db_url = os.getenv("DATABASE_URL", "").strip()
if not db_url:
    # ローカル用（data/app.db）: GitHub/Render でも存在OK
    os.makedirs("data", exist_ok=True)
    db_url = "sqlite:///data/app.db"

# Render の Postgres は postgresql:// を返す。psycopg ドライバ指定を足す
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
elif db_url.startswith("postgresql://") and "+psycopg" not in db_url:
    db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ------------ 例: 履歴テーブルの最小モデル（既存があればそのままでOK） -------------
class ProfitHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    platform = db.Column(db.String(50), nullable=True)
    profit = db.Column(db.Integer, nullable=False, default=0)

# 初回起動時にテーブル作成（既存テーブルがあれば何もしません）
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        # DB接続エラーはイベントログに出すだけ（画面は落とさない）
        print("DB init error:", e)

# ------------ テンプレ共通：円表示フィルタ -------------
@app.template_filter("yen")
def yen(v):
    try:
        return f"¥{int(v):,}"
    except Exception:
        return "¥0"

# ------------ ルーティング（表示系はプレースホルダのまま） -------------
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
    # 例：DB読み込み（ページが空でも動作確認用）
    items = ProfitHistory.query.order_by(ProfitHistory.id.desc()).limit(20).all()
    return render_template("pages/history.html", items=items)

@app.route("/ranking")
def ranking():
    return render_template("pages/ranking.html")

@app.route("/notifications")
def notifications():
    return render_template("pages/notifications.html")

@app.route("/ocr", methods=["GET", "POST"])
def ocr():
    return render_template("pages/ocr.html")

@app.route("/suppliers")
def suppliers():
    return render_template("pages/suppliers.html")

@app.route("/setting")
def setting():
    return render_template("pages/setting.html")

# エラーハンドラ
@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html"), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template("errors/500.html"), 500

# Render のヘルスチェック用
@app.route("/health")
def health():
    return "ok", 200

if __name__ == "__main__":
    # ローカル実行用
    app.run(host="0.0.0.0", port=5000, debug=True)
