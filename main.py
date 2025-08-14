import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# -----------------------------------------------------------------------------
# Flask 基本設定
# -----------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "research-navi-dev")

# DATABASE_URL を取得（Render の環境変数）/ ローカルは SQLite に自動フォールバック
raw_db_url = os.getenv("DATABASE_URL", "sqlite:///data/app.db")
# Render の Internal URL は "postgresql://..." なので、ドライバ指定を付与
if raw_db_url.startswith("postgresql://"):
    raw_db_url = raw_db_url.replace("postgresql://", "postgresql+psycopg://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = raw_db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# 接続ヘルスチェック（Freeプランやスリープ復帰対策）
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}

db = SQLAlchemy(app)

# -----------------------------------------------------------------------------
# モデル
# -----------------------------------------------------------------------------
class ProfitHistory(db.Model):
    __tablename__ = "profit_history"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)          # 商品名
    platform = db.Column(db.String(50), nullable=False)        # プラットフォーム
    price = db.Column(db.Integer, nullable=False, default=0)   # 販売価格
    cost = db.Column(db.Integer, nullable=False, default=0)    # 仕入れ
    ship = db.Column(db.Integer, nullable=False, default=0)    # 送料
    fee = db.Column(db.Integer, nullable=False, default=0)     # 手数料(円)
    profit = db.Column(db.Integer, nullable=False, default=0)  # 利益(円)
    margin = db.Column(db.Float, nullable=False, default=0.0)  # 利益率(%)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<ProfitHistory id={self.id} name={self.name} profit={self.profit}>"

# -----------------------------------------------------------------------------
# ユーティリティ
# -----------------------------------------------------------------------------
def calc_profit(price: int, cost: int, ship: int, fee: int):
    """単純計算：利益額と利益率(%)を返す"""
    profit = int(price) - int(cost) - int(ship) - int(fee)
    margin = round((profit / int(price) * 100.0), 2) if int(price) > 0 else 0.0
    return profit, margin

@app.template_filter("yen")
def yen(v):
    try:
        return f"¥{int(v):,}"
    except Exception:
        return v

# -----------------------------------------------------------------------------
# まずは DB を用意（存在しなければ作成）
# -----------------------------------------------------------------------------
with app.app_context():
    db.create_all()

# -----------------------------------------------------------------------------
# ルーティング（テンプレは既存のまま使用）
# -----------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("pages/home.html")

@app.route("/search")
def search():
    return render_template("pages/search.html")

@app.route("/profit", methods=["GET", "POST"])
def profit():
    """
    POST されたらDBに保存。
    期待するフォーム項目：
      name, platform, price, cost, ship, fee
    """
    if request.method == "POST":
        name = request.form.get("name", "").strip() or "商品名未設定"
        platform = request.form.get("platform", "").strip() or "Unknown"
        price = int(request.form.get("price", 0) or 0)
        cost = int(request.form.get("cost", 0) or 0)
        ship = int(request.form.get("ship", 0) or 0)
        fee = int(request.form.get("fee", 0) or 0)

        p, m = calc_profit(price, cost, ship, fee)
        row = ProfitHistory(
            name=name, platform=platform,
            price=price, cost=cost, ship=ship, fee=fee,
            profit=p, margin=m
        )
        db.session.add(row)
        db.session.commit()
        flash(f"保存しました：{name} / 利益 {p:,} 円（{m}%）")
        return redirect(url_for("history"))

    return render_template("pages/profit.html")

@app.route("/history")
def history():
    rows = ProfitHistory.query.order_by(ProfitHistory.created_at.desc()).limit(200).all()
    return render_template("pages/history.html", rows=rows)

@app.route("/ranking")
def ranking():
    # 直近の利益上位（簡易）
    rows = (ProfitHistory.query
            .order_by(ProfitHistory.profit.desc())
            .limit(10).all())
    return render_template("pages/ranking.html", rows=rows)

@app.route("/notifications")
def notifications():
    return render_template("pages/notifications.html")

@app.route("/ocr", methods=["GET", "POST"])
def ocr():
    return render_template("pages/ocr.html")

@app.route("/suppliers")
def suppliers():
    return render_template("pages/suppliers.html")

@app.route("/setting", methods=["GET", "POST"])
def setting():
    return render_template("pages/setting.html")

# ---- 管理/ニュース/ポリシー/その他（テンプレだけ呼び出し） ------------------------
@app.route("/about")
def about():
    return render_template("pages/about.html")

@app.route("/faq")
def faq():
    return render_template("pages/faq.html")

@app.route("/support")
def support():
    return render_template("pages/support.html")

@app.route("/dashboard")
def dashboard():
    return render_template("pages/dashboard.html")

@app.route("/report")
def report():
    return render_template("pages/report.html")

# -----------------------------------------------------------------------------
# デバッグ用ツール（接続確認）
# -----------------------------------------------------------------------------
@app.route("/dbcheck")
def dbcheck():
    try:
        v = db.session.execute(text("SELECT 1")).scalar_one()
        return f"DB OK ({v}) / URI: {app.config['SQLALCHEMY_DATABASE_URI'].split('@')[0]}..."
    except Exception as e:
        return f"DB ERROR: {e}", 500

# -----------------------------------------------------------------------------
# エラーハンドラ
# -----------------------------------------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("errors/500.html"), 500

# -----------------------------------------------------------------------------
# Render / Waitress 用エントリポイント
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # ローカル実行用（Flask の組み込みサーバ）
    app.run(host="0.0.0.0", port=5000, debug=True)

