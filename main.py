import os, csv, json
from io import StringIO, BytesIO
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# -----------------------------------------------------------------------------
# Flask / DB
# -----------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "research-navi-dev")

raw_db_url = os.getenv("DATABASE_URL", "sqlite:///data/app.db")
# Render の Postgres を SQLAlchemy で使える形式へ
if raw_db_url.startswith("postgresql://"):
    raw_db_url = raw_db_url.replace("postgresql://", "postgresql+psycopg://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = raw_db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}
db = SQLAlchemy(app)

# -----------------------------------------------------------------------------
# モデル
# -----------------------------------------------------------------------------
class ProfitHistory(db.Model):
    __tablename__ = "profit_history"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False, default=0)
    cost = db.Column(db.Integer, nullable=False, default=0)
    ship = db.Column(db.Integer, nullable=False, default=0)
    fee = db.Column(db.Integer, nullable=False, default=0)
    profit = db.Column(db.Integer, nullable=False, default=0)
    margin = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    kind = db.Column(db.String(20), nullable=False, default="info")   # profit/pricedrop/stock/info
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, default="")
    meta_json = db.Column(db.Text, default="{}")
    unread = db.Column(db.Boolean, default=True, nullable=False)
    snooze_until = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    @property
    def meta(self):
        try:
            return json.loads(self.meta_json or "{}")
        except Exception:
            return {}

# -----------------------------------------------------------------------------
# テンプレフィルタ
# -----------------------------------------------------------------------------
def calc_profit(price: int, cost: int, ship: int, fee: int):
    p = int(price) - int(cost) - int(ship) - int(fee)
    m = round((p / int(price) * 100.0), 2) if int(price) > 0 else 0.0
    return p, m

@app.template_filter("yen")
def yen(v):
    try: return f"¥{int(v):,}"
    except: return v

@app.template_filter("fmt")
def fmt(dt):
    try: return dt.strftime("%Y-%m-%d %H:%M")
    except: return dt

# -----------------------------------------------------------------------------
# 初期化
# -----------------------------------------------------------------------------
with app.app_context():
    db.create_all()
    # 初回だけデモ通知
    if Notification.query.count() == 0:
        demo = [
            Notification(kind="profit", title="利益アラート：Switch 有機EL（利益 ¥8,900 / 21%）",
                         body="条件：利益≥¥8,000 AND 利益率≥18% AND 回転≥70",
                         meta_json=json.dumps({"販売":"¥44,800","仕入":"¥33,000","在庫":"◯（出品者 6）"}, ensure_ascii=False)),
            Notification(kind="pricedrop", title="値下げ検知：Anker 100W 充電器（-12%）",
                         body="前回比 -¥980 / クーポンでさらに -¥500",
                         meta_json=json.dumps({"最安":"¥6,980","実質":"¥6,480"}, ensure_ascii=False)),
        ]
        db.session.add_all(demo); db.session.commit()

# -----------------------------------------------------------------------------
# ルーティング
# -----------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("pages/home.html")

@app.route("/search")
def search():
    return render_template("pages/search.html")

@app.route("/profit", methods=["GET", "POST"])
def profit():
    if request.method == "POST":
        name = (request.form.get("name") or "商品名未設定").strip()
        platform = (request.form.get("platform") or "Unknown").strip()
        price = int(request.form.get("price") or 0)
        cost  = int(request.form.get("cost")  or 0)
        ship  = int(request.form.get("ship")  or 0)
        fee   = int(request.form.get("fee")   or 0)

        p, m = calc_profit(price, cost, ship, fee)

        # 履歴保存
        row = ProfitHistory(name=name, platform=platform, price=price, cost=cost, ship=ship, fee=fee, profit=p, margin=m)
        db.session.add(row)
        db.session.commit()  # id確定

        # ==== ここから 自動通知作成 ==========================================
        threshold = int(os.getenv("PROFIT_THRESHOLD", "5000") or 0)
        margin_min = float(os.getenv("MARGIN_THRESHOLD", "0") or 0)  # 任意
        cond_ok = (p >= threshold) and (m >= margin_min)

        if cond_ok:
            title = f"利益アラート：{name}（利益 ¥{p:,} / {m}%）"
            body  = f"条件：利益≥¥{threshold:,}" + (f" AND 利益率≥{margin_min}%" if margin_min > 0 else "")
            meta  = {
                "販売": f"¥{price:,}",
                "仕入": f"¥{cost:,}",
                "送料": f"¥{ship:,}",
                "手数料": f"¥{fee:,}",
                "PF": platform,
                "履歴ID": row.id,
            }
            n = Notification(kind="profit", title=title, body=body, meta_json=json.dumps(meta, ensure_ascii=False))
            db.session.add(n)
            db.session.commit()
        # ==== ここまで ======================================================

        flash(f"保存しました：{name} / 利益 {p:,} 円（{m}%）")
        return redirect(url_for("history"))

    return render_template("pages/profit.html")

@app.route("/history")
def history():
    rows = ProfitHistory.query.order_by(ProfitHistory.created_at.desc()).limit(200).all()
    return render_template("pages/history.html", rows=rows)

@app.route("/export/history.csv")
def export_history():
    sio = StringIO(); w = csv.writer(sio)
    w.writerow(["日時","商品名","PF","販売","仕入","送料","手数料","利益","利益率(%)"])
    for r in ProfitHistory.query.order_by(ProfitHistory.created_at.desc()).all():
        w.writerow([r.created_at.strftime("%Y-%m-%d %H:%M"), r.name, r.platform, r.price, r.cost, r.ship, r.fee, r.profit, r.margin])
    data = sio.getvalue().encode("utf-8-sig")
    fname = f"profit_history_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.csv"
    return send_file(BytesIO(data), as_attachment=True, download_name=fname, mimetype="text/csv; charset=utf-8")

@app.route("/ranking")
def ranking():
    days = (request.args.get("days") or "30").lower()
    q = ProfitHistory.query; label = "直近30日"
    if days != "all":
        try:
            n = int(days); since = datetime.utcnow() - timedelta(days=n)
            q = q.filter(ProfitHistory.created_at >= since); label = f"直近{n}日"
        except: pass
    else:
        label = "全期間"
    rows = q.order_by(ProfitHistory.profit.desc()).limit(50).all()
    return render_template("pages/ranking.html", rows=rows, days=days, label=label)

# ---- 通知（表示/既読/スヌーズ） ----------------------------------------------
@app.route("/notifications")
def notifications():
    now = datetime.utcnow()
    rows = (Notification.query
            .filter((Notification.snooze_until.is_(None)) | (Notification.snooze_until <= now))
            .order_by(Notification.unread.desc(), Notification.created_at.desc())
            .limit(200).all())
    return render_template("pages/notifications.html", rows=rows)

@app.post("/api/notifications/mark_read")
def api_notif_mark_read():
    data = request.get_json(silent=True) or {}
    ids = data.get("ids") or []
    if not isinstance(ids, list): ids = [ids]
    q = Notification.query.filter(Notification.id.in_(ids))
    cnt = 0
    for n in q:
        if n.unread: n.unread = False; cnt += 1
    db.session.commit()
    return jsonify(ok=True, updated=cnt)

@app.post("/api/notifications/snooze")
def api_notif_snooze():
    data = request.get_json(silent=True) or {}
    nid = int(data.get("id") or 0)
    minutes = int(data.get("minutes") or 60)
    n = Notification.query.get(nid)
    if not n: return jsonify(ok=False, error="not_found"), 404
    n.snooze_until = datetime.utcnow() + timedelta(minutes=minutes)
    db.session.commit()
    return jsonify(ok=True, snooze_until=n.snooze_until.isoformat())

# ---- その他ページ -------------------------------------------------------------
@app.route("/ocr", methods=["GET", "POST"])
def ocr():
    return render_template("pages/ocr.html")

@app.route("/suppliers")
def suppliers():
    return render_template("pages/suppliers.html")

@app.route("/setting", methods=["GET", "POST"])
def setting():
    return render_template("pages/setting.html")

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

# ---- DBチェック・エラー -------------------------------------------------------
@app.route("/dbcheck")
def dbcheck():
    try:
        v = db.session.execute(text("SELECT 1")).scalar_one()
        return f"DB OK ({v}) / URI: {app.config['SQLALCHEMY_DATABASE_URI'].split('@')[0]}..."
    except Exception as e:
        return f"DB ERROR: {e}", 500

@app.errorhandler(404)
def _404(e): return render_template("errors/404.html"), 404

@app.errorhandler(500)
def _500(e): return render_template("errors/500.html"), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
