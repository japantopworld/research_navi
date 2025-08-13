# main.py
import os
from datetime import datetime, timezone
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from io import StringIO
import csv

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.getenv("SECRET_KEY", "research-navi-dev")

# --- DB 接続（Render の環境変数 DATABASE_URL を使う。無ければローカル SQLite） ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/app.db")
# Render の URL は "postgresql://" または "postgres://" が来る。SQLAlchemy は "postgresql" を期待。
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# ---------------------------- モデル ----------------------------
class Setting(db.Model):
    __tablename__ = "settings"
    id = db.Column(db.Integer, primary_key=True)
    mail_enabled = db.Column(db.Boolean, default=False)
    mail_provider = db.Column(db.String(20), default="gmail")
    mail_from = db.Column(db.String(255))
    mail_pass = db.Column(db.String(255))
    mail_to = db.Column(db.String(1000))  # カンマ区切り
    profit_threshold = db.Column(db.Integer, default=5000)  # 通知しきい値（円）

class ProfitHistory(db.Model):
    __tablename__ = "profit_history"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    platform = db.Column(db.String(50), default="その他")
    price = db.Column(db.Integer, default=0)   # 販売価格
    cost = db.Column(db.Integer, default=0)    # 仕入
    ship = db.Column(db.Integer, default=0)    # 送料
    fee  = db.Column(db.Integer, default=0)    # 手数料（円）
    profit = db.Column(db.Integer, default=0)  # 最終利益（円）
    margin = db.Column(db.Float, default=0.0)  # 利益率（%）
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


# ---------------------------- 初期化 ----------------------------
def init_db():
    db.create_all()
    # 設定レコードが無ければ1件作る
    if not Setting.query.first():
        s = Setting(
            mail_enabled=False,
            mail_provider="gmail",
            mail_from="",
            mail_pass="",
            mail_to="",
            profit_threshold=5000,
        )
        db.session.add(s)
        db.session.commit()

@app.template_filter("yen")
def yen(v):
    try:
        return f"¥{int(v):,}"
    except Exception:
        return "¥0"

with app.app_context():
    init_db()


# ---------------------------- ルーティング（最小セット） ----------------------------
@app.route("/")
def home():
    return render_template("pages/home.html")

@app.route("/profit", methods=["GET", "POST"])
def profit():
    if request.method == "POST":
        # 入力値
        name = request.form.get("name", "").strip() or "商品"
        platform = request.form.get("platform", "その他")
        price = int(request.form.get("price") or 0)
        cost  = int(request.form.get("cost") or 0)
        ship  = int(request.form.get("ship") or 0)
        fee   = int(request.form.get("fee") or 0)

        profit_val = price - cost - ship - fee
        margin = round((profit_val / price) * 100, 2) if price else 0.0

        rec = ProfitHistory(
            name=name, platform=platform,
            price=price, cost=cost, ship=ship, fee=fee,
            profit=profit_val, margin=margin
        )
        db.session.add(rec)
        db.session.commit()

        flash(f"保存しました：{name} / 利益 {profit_val:,} 円（利益率 {margin}%）")

        return redirect(url_for("history"))

    return render_template("pages/profit.html")

@app.route("/history")
def history():
    rows = ProfitHistory.query.order_by(ProfitHistory.created_at.desc()).limit(500).all()
    return render_template("pages/history.html", rows=rows)

@app.route("/history/export")
def history_export():
    rows = ProfitHistory.query.order_by(ProfitHistory.created_at.desc()).all()
    sio = StringIO()
    w = csv.writer(sio)
    w.writerow(["日時","商品名","プラットフォーム","販売価格","仕入","送料","手数料","利益","利益率"])
    for r in rows:
        w.writerow([
            r.created_at.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M"),
            r.name, r.platform, r.price, r.cost, r.ship, r.fee, r.profit, r.margin
        ])
    data = sio.getvalue().encode("utf-8-sig")
    return send_file(
        bytes(data),
        mimetype="text/csv; charset=utf-8",
        as_attachment=True,
        download_name="profit_history.csv"
    )

@app.route("/notifications")
def notifications():
    s = Setting.query.first()
    threshold = s.profit_threshold if s else 5000
    hits = ProfitHistory.query.filter(ProfitHistory.profit >= threshold)\
            .order_by(ProfitHistory.created_at.desc()).limit(50).all()
    return render_template("pages/notifications.html", hits=hits, threshold=threshold)

@app.route("/setting", methods=["GET","POST"])
def setting():
    s = Setting.query.first()
    if request.method == "POST":
        # 空で送られたらそのまま（パスワードはブランクを維持）
        s.mail_enabled = bool(request.form.get("mail_enabled"))
        s.mail_provider = request.form.get("mail_provider") or "gmail"
        s.mail_from = request.form.get("mail_from", "")
        s.mail_to   = request.form.get("mail_to", "")
        if request.form.get("mail_pass", ""):
            s.mail_pass = request.form.get("mail_pass")
        s.profit_threshold = int(request.form.get("profit_threshold") or 5000)
        db.session.commit()
        flash("設定を保存しました。")
        return redirect(url_for("setting"))
    return render_template("pages/setting.html", s=s)

# そのほか雛形ページ（必要なら既存テンプレをそのまま使用）
@app.route("/search")
def search(): return render_template("pages/search.html")
@app.route("/ranking")
def ranking(): return render_template("pages/ranking.html")
@app.route("/ocr")
def ocr(): return render_template("pages/ocr.html")
@app.route("/suppliers")
def suppliers(): return render_template("pages/suppliers.html")

@app.errorhandler(404)
def not_found(e): return render_template("errors/404.html"), 404
@app.errorhandler(500)
def err500(e):   return render_template("errors/500.html"), 500

# Render は gunicorn で起動するので if __name__ はローカル動作用
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
