# main.py
import os, csv, json, ssl, smtplib
from io import StringIO, BytesIO
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, send_file, jsonify
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, func

# =============================================================================
# Flask / DB 基本設定
# =============================================================================
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "research-navi-dev")

raw_db_url = os.getenv("DATABASE_URL", "sqlite:///data/app.db")
# Render(Postgres)の "postgresql://" → SQLAlchemy用 "postgresql+psycopg://"
if raw_db_url.startswith("postgresql://"):
    raw_db_url = raw_db_url.replace("postgresql://", "postgresql+psycopg://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = raw_db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}
db = SQLAlchemy(app)

# =============================================================================
# モデル
# =============================================================================
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
    kind = db.Column(db.String(20), nullable=False, default="info")  # profit/pricedrop/stock/info
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

class AppSettings(db.Model):
    __tablename__ = "app_settings"
    id = db.Column(db.Integer, primary_key=True)
    mail_enabled = db.Column(db.Boolean, nullable=False, default=False)
    mail_provider = db.Column(db.String(50), nullable=False, default="gmail")
    mail_from = db.Column(db.String(255), nullable=False, default="")
    mail_to = db.Column(db.String(1000), nullable=False, default="")   # カンマ区切り
    mail_pass = db.Column(db.String(255), nullable=False, default="")
    profit_threshold = db.Column(db.Integer, nullable=False, default=5000)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    @staticmethod
    def get() -> "AppSettings":
        s = AppSettings.query.get(1)
        if not s:
            s = AppSettings(id=1, mail_enabled=False, mail_provider="gmail",
                            mail_from="", mail_to="", mail_pass="",
                            profit_threshold=5000)
            db.session.add(s)
            db.session.commit()
        return s

# =============================================================================
# ユーティリティ / テンプレフィルタ
# =============================================================================
def _to_int(x):
    try:
        if x is None: return 0
        if isinstance(x, (int, float)): return int(round(x))
        s = str(x).replace(",", "").replace("¥", "").replace("円", "").strip()
        if s == "": return 0
        return int(round(float(s)))
    except Exception:
        return 0

def calc_profit(price: int, cost: int, ship: int, fee: int):
    p = int(price) - int(cost) - int(ship) - int(fee)
    m = round((p / int(price) * 100.0), 2) if int(price) > 0 else 0.0
    return p, m

def estimate_fee(platform: str, price: int) -> int:
    """PF別の簡易手数料。"""
    pf = (platform or "").lower()
    pr = int(price or 0)
    if pr <= 0: return 0
    if "amazon" in pf or "アマゾン" in pf:
        return round(pr * 0.10) + 100   # 10% + 100円（簡易）
    if "楽天" in platform or "rakuten" in pf:
        return round(pr * 0.07)         # 7%
    if "ヤフ" in platform or "yahoo" in pf:
        return round(pr * 0.08)         # 8%
    if "メルカリ" in platform or "mercari" in pf:
        return round(pr * 0.10)         # 10%
    return round(pr * 0.05)             # その他 5%

@app.template_filter("yen")
def yen(v):
    try:
        return f"¥{int(v):,}"
    except Exception:
        return v

@app.template_filter("fmt")
def fmt(dt):
    try:
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return dt

def _parse_date(s: str):
    if not s: return None
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d", "%Y/%m/%d %H:%M", "%Y/%m/%d"):
        try:
            return datetime.strptime(s.strip(), fmt)
        except Exception:
            continue
    return None

# ---- メール送信 ---------------------------------------------------------------
def _smtp_profile(provider: str):
    table = {
        "gmail":   ("smtp.gmail.com", 465, True,  False),
        "icloud":  ("smtp.mail.me.com", 587, False, True),
        "outlook": ("smtp.office365.com", 587, False, True),
        "yahoo":   ("smtp.mail.yahoo.co.jp", 465, True, False),
    }
    if provider in table:
        return table[provider]
    if "." in provider:
        return (provider, 587, False, True)
    return table["gmail"]

def send_mail_by_settings(subject: str, html: str, text_alt: str = ""):
    s = AppSettings.get()
    if not s.mail_enabled:
        return False, "disabled"
    if not (s.mail_from and s.mail_pass and s.mail_to):
        return False, "settings_incomplete"

    host, port, use_ssl, use_tls = _smtp_profile((s.mail_provider or "gmail").lower())

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = s.mail_from
    msg["To"]   = s.mail_to
    if text_alt:
        msg.attach(MIMEText(text_alt, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        if use_ssl:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(host, port, context=context) as smtp:
                smtp.login(s.mail_from, s.mail_pass)
                smtp.sendmail(s.mail_from, [x.strip() for x in s.mail_to.split(",") if x.strip()], msg.as_string())
        else:
            with smtplib.SMTP(host, port) as smtp:
                if use_tls:
                    smtp.starttls()
                smtp.login(s.mail_from, s.mail_pass)
                smtp.sendmail(s.mail_from, [x.strip() for x in s.mail_to.split(",") if x.strip()], msg.as_string())
        return True, "sent"
    except Exception as e:
        print(f"[MAIL ERROR] {e}")
        return False, str(e)

# =============================================================================
# 初期化
# =============================================================================
with app.app_context():
    db.create_all()
    AppSettings.get()

# =============================================================================
# レポート集計
# =============================================================================
def _report_range(kind: str):
    # Asia/Tokyo の終日を意識（ただしDBはUTC保存想定）
    now = datetime.utcnow()
    if kind == "weekly":
        start = now - timedelta(days=7)
        title = "週次レポート（直近7日）"
    elif kind == "monthly":
        start = now - timedelta(days=30)
        title = "月次レポート（直近30日）"
    else:
        start = now - timedelta(days=7)
        title = "週次レポート（直近7日）"
    end = now
    return title, start, end

def make_report(start_dt: datetime, end_dt: datetime):
    q = (db.session.query(ProfitHistory)
         .filter(ProfitHistory.created_at >= start_dt)
         .filter(ProfitHistory.created_at <  end_dt))

    # トータル
    sum_price  = db.session.query(func.coalesce(func.sum(ProfitHistory.price), 0)).filter(
        ProfitHistory.created_at >= start_dt, ProfitHistory.created_at < end_dt).scalar() or 0
    sum_profit = db.session.query(func.coalesce(func.sum(ProfitHistory.profit), 0)).filter(
        ProfitHistory.created_at >= start_dt, ProfitHistory.created_at < end_dt).scalar() or 0
    avg_margin = db.session.query(func.coalesce(func.avg(ProfitHistory.margin), 0.0)).filter(
        ProfitHistory.created_at >= start_dt, ProfitHistory.created_at < end_dt).scalar() or 0.0
    count_rows = q.count()

    # PF別
    by_pf = (db.session.query(
                ProfitHistory.platform.label("platform"),
                func.coalesce(func.sum(ProfitHistory.profit),0).label("sum_profit"),
                func.count(ProfitHistory.id).label("cnt"))
             .filter(ProfitHistory.created_at >= start_dt, ProfitHistory.created_at < end_dt)
             .group_by(ProfitHistory.platform)
             .order_by(func.sum(ProfitHistory.profit).desc())
             .all())

    # TOP商品
    top = (db.session.query(
                ProfitHistory.name.label("name"),
                ProfitHistory.platform.label("platform"),
                func.coalesce(func.sum(ProfitHistory.profit),0).label("sum_profit"),
                func.count(ProfitHistory.id).label("cnt"),
                func.min(ProfitHistory.created_at).label("first_at"),
                func.max(ProfitHistory.created_at).label("last_at"))
           .filter(ProfitHistory.created_at >= start_dt, ProfitHistory.created_at < end_dt)
           .group_by(ProfitHistory.name, ProfitHistory.platform)
           .order_by(func.sum(ProfitHistory.profit).desc())
           .limit(10).all())

    return {
        "sum_price": int(sum_price or 0),
        "sum_profit": int(sum_profit or 0),
        "avg_margin": round(float(avg_margin or 0), 2),
        "count_rows": int(count_rows or 0),
        "by_pf": by_pf,
        "top": top,
    }

def render_report_html(title: str, start_dt: datetime, end_dt: datetime):
    stats = make_report(start_dt, end_dt)
    return render_template(
        "email/report_summary.html",
        title=title,
        start=start_dt, end=end_dt,
        stats=stats,
        generated=datetime.utcnow()
    )

def send_report(kind: str):
    title, start_dt, end_dt = _report_range(kind)
    html = render_report_html(title, start_dt, end_dt)
    subj = f"【リサーチナビ】{title}"
    ok, info = send_mail_by_settings(subj, html, f"{title}")
    return ok, info

# =============================================================================
# ルーティング：ページ
# =============================================================================
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
        price = _to_int(request.form.get("price"))
        cost  = _to_int(request.form.get("cost"))
        ship  = _to_int(request.form.get("ship"))

        fee_mode = (request.form.get("fee_mode") or "auto").lower()
        if fee_mode == "auto":
            fee = estimate_fee(platform, price)
        else:
            fee = _to_int(request.form.get("fee"))

        p, m = calc_profit(price, cost, ship, fee)

        row = ProfitHistory(name=name, platform=platform, price=price,
                            cost=cost, ship=ship, fee=fee, profit=p, margin=m)
        db.session.add(row); db.session.commit()

        s = AppSettings.get()
        threshold = int(s.profit_threshold or 0)
        if p >= threshold:
            meta = {"販売": f"¥{price:,}","仕入": f"¥{cost:,}","送料": f"¥{ship:,}",
                    "手数料": f"¥{fee:,}","PF": platform,"履歴ID": row.id}
            n = Notification(kind="profit",
                             title=f"利益アラート：{name}（利益 ¥{p:,} / {m}%）",
                             body=f"条件：利益≥¥{threshold:,}",
                             meta_json=json.dumps(meta, ensure_ascii=False))
            db.session.add(n); db.session.commit()

            try:
                html = render_template("email/profit_notice.html",
                    name=name, platform=platform, profit_val=p, margin=m,
                    price=price, cost=cost, ship=ship, fee_calc=fee,
                    threshold=threshold, now=datetime.utcnow().strftime("%Y-%m-%d %H:%M"))
            except Exception:
                html = (f"<h2>利益アラート</h2>"
                        f"<p>商品名：{name} / PF：{platform}</p>"
                        f"<p>利益：¥{p:,}（{m}%）</p>"
                        f"<p>販売：¥{price:,} / 仕入：¥{cost:,} / 送料：¥{ship:,} / 手数料：¥{fee:,}</p>")
            subj = f"【RN】利益アラート：{name} 利益 ¥{p:,}（{m}%）"
            send_mail_by_settings(subj, html, f"[利益アラート] {name} / 利益 ¥{p:,}")

        flash(f"保存しました：{name} / 利益 {p:,} 円（{m}%）")
        return redirect(url_for("history"))
    return render_template("pages/profit.html")

# ---------- 履歴：検索/絞り込み & 表示 ----------------------------------------
def _build_history_query(args):
    q = ProfitHistory.query
    label = []
    start_s = (args.get("start") or "").strip()
    end_s   = (args.get("end") or "").strip()
    start_dt = _parse_date(start_s)
    end_dt   = _parse_date(end_s)
    if start_dt:
        q = q.filter(ProfitHistory.created_at >= start_dt)
        label.append(f"{start_dt.strftime('%Y-%m-%d')}〜")
    if end_dt:
        end_next = end_dt + timedelta(days=1)
        q = q.filter(ProfitHistory.created_at < end_next)
        if not start_dt:
            label.append(f"〜{end_dt.strftime('%Y-%m-%d')}")
        else:
            label[-1] = f"{start_dt.strftime('%Y-%m-%d')}〜{end_dt.strftime('%Y-%m-%d')}"
    pf = (args.get("platform") or "").strip()
    if pf and pf.lower() != "all":
        q = q.filter(ProfitHistory.platform == pf)
        label.append(f"PF={pf}")
    kw = (args.get("keyword") or "").strip()
    if kw:
        q = q.filter(ProfitHistory.name.ilike(f"%{kw}%"))
        label.append(f"KW='{kw}'")
    try:
        min_profit = int(args.get("min_profit") or 0)
    except Exception:
        min_profit = 0
    if min_profit > 0:
        q = q.filter(ProfitHistory.profit >= min_profit)
        label.append(f"利益≥¥{min_profit:,}")
    label_text = " / ".join(label) if label else "全件"
    return q, label_text, {"start": start_s, "end": end_s, "platform": pf, "keyword": kw, "min_profit": min_profit}

@app.route("/history")
def history():
    platforms = [r[0] for r in db.session.query(ProfitHistory.platform).distinct().all()]
    q, label, params = _build_history_query(request.args)
    total = q.count()
    rows = q.order_by(ProfitHistory.created_at.desc()).limit(500).all()
    return render_template("pages/history.html",
                           rows=rows, total=total, label=label,
                           params=params, platforms=platforms)

@app.route("/export/history.csv")
def export_history():
    q, _, _ = _build_history_query(request.args)
    q = q.order_by(ProfitHistory.created_at.desc())
    sio = StringIO(); w = csv.writer(sio)
    w.writerow(["日時","商品名","PF","販売","仕入","送料","手数料","利益","利益率(%)"])
    for r in q.all():
        w.writerow([r.created_at.strftime("%Y-%m-%d %H:%M"),
                    r.name, r.platform, r.price, r.cost, r.ship, r.fee, r.profit, r.margin])
    data = sio.getvalue().encode("utf-8-sig")
    fname = f"profit_history_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.csv"
    return send_file(BytesIO(data), as_attachment=True,
                     download_name=fname, mimetype="text/csv; charset=utf-8")

# ---------- ランキング ----------------------------------------------------------
def _build_ranking_query(args):
    q = db.session.query(
        ProfitHistory.name.label("name"),
        ProfitHistory.platform.label("platform"),
        func.count(ProfitHistory.id).label("cnt"),
        func.sum(ProfitHistory.price).label("sum_price"),
        func.sum(ProfitHistory.profit).label("sum_profit"),
        func.avg(ProfitHistory.margin).label("avg_margin"),
        func.min(ProfitHistory.created_at).label("first_at"),
        func.max(ProfitHistory.created_at).label("last_at"),
    )

    label = []
    start_s = (args.get("start") or "").strip()
    end_s   = (args.get("end") or "").strip()
    start_dt = _parse_date(start_s)
    end_dt   = _parse_date(end_s)
    if start_dt:
        q = q.filter(ProfitHistory.created_at >= start_dt)
        label.append(f"{start_dt.strftime('%Y-%m-%d')}〜")
    if end_dt:
        end_next = end_dt + timedelta(days=1)
        q = q.filter(ProfitHistory.created_at < end_next)
        if not start_dt:
            label.append(f"〜{end_dt.strftime('%Y-%m-%d')}")
        else:
            label[-1] = f"{start_dt.strftime('%Y-%m-%d')}〜{end_dt.strftime('%Y-%m-%d')}"

    pf = (args.get("platform") or "").strip()
    if pf and pf.lower() != "all":
        q = q.filter(ProfitHistory.platform == pf)
        label.append(f"PF={pf}")

    kw = (args.get("keyword") or "").strip()
    if kw:
        q = q.filter(ProfitHistory.name.ilike(f"%{kw}%"))
        label.append(f"KW='{kw}'")

    try:
        min_sum_profit = int(args.get("min_total_profit") or 0)
    except Exception:
        min_sum_profit = 0

    q = (q.group_by(ProfitHistory.name, ProfitHistory.platform)
           .order_by(func.sum(ProfitHistory.profit).desc()))

    if min_sum_profit > 0:
        label.append(f"合計利益≥¥{min_sum_profit:,}")

    params = {
        "start": start_s, "end": end_s, "platform": pf,
        "keyword": kw, "min_total_profit": min_sum_profit
    }
    return q, " / ".join(label) if label else "全期間・全PF", params

@app.route("/ranking")
def ranking():
    platforms = [r[0] for r in db.session.query(ProfitHistory.platform).distinct().all()]
    q, label, params = _build_ranking_query(request.args)
    rows_all = q.all()
    min_tp = params.get("min_total_profit") or 0
    if min_tp:
        rows_all = [r for r in rows_all if (r.sum_profit or 0) >= min_tp]
    rows_sorted = sorted(rows_all, key=lambda r: (r.sum_profit or 0), reverse=True)
    top3 = rows_sorted[:3]
    rest = rows_sorted[3:50]
    total = len(rows_sorted)
    return render_template("pages/ranking.html",
                           top3=top3, rows=rest, total=total,
                           label=label, platforms=platforms, params=params)

@app.route("/export/ranking.csv")
def export_ranking():
    q, _, params = _build_ranking_query(request.args)
    rows = q.all()
    min_tp = params.get("min_total_profit") or 0
    if min_tp:
        rows = [r for r in rows if (r.sum_profit or 0) >= min_tp]

    sio = StringIO(); w = csv.writer(sio)
    w.writerow(["商品名","PF","件数","売上合計","利益合計","平均利益率(%)","初回","最終"])
    for r in sorted(rows, key=lambda x:(x.sum_profit or 0), reverse=True):
        w.writerow([
            r.name, r.platform, r.cnt,
            int(r.sum_price or 0), int(r.sum_profit or 0),
            round(float(r.avg_margin or 0.0), 2),
            (r.first_at or datetime.utcnow()).strftime("%Y-%m-%d"),
            (r.last_at  or datetime.utcnow()).strftime("%Y-%m-%d"),
        ])
    data = sio.getvalue().encode("utf-8-sig")
    fname = f"ranking_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.csv"
    return send_file(BytesIO(data), as_attachment=True,
                     download_name=fname, mimetype="text/csv; charset=utf-8")

# ---------- 通知（表示/既読/スヌーズ） ----------------------------------------
@app.route("/notifications")
def notifications():
    now = datetime.utcnow()
    rows = (Notification.query
            .filter((Notification.snooze_until.is_(None)) |
                    (Notification.snooze_until <= now))
            .order_by(Notification.unread.desc(),
                      Notification.created_at.desc())
            .limit(200).all())
    return render_template("pages/notifications.html", rows=rows)

@app.post("/api/notifications/mark_read")
def api_notif_mark_read():
    data = request.get_json(silent=True) or {}
    ids = data.get("ids") or []
    if not isinstance(ids, list): ids = [ids]
    q = Notification.query.filter(Notification.id.in_(ids))
    updated = 0
    for n in q:
        if n.unread:
            n.unread = False; updated += 1
    db.session.commit()
    return jsonify(ok=True, updated=updated)

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

# ---------- レポート：プレビュー & 送信 ----------------------------------------
@app.get("/reports/weekly/preview")
def report_weekly_preview():
    title, start_dt, end_dt = _report_range("weekly")
    html = render_report_html(title, start_dt, end_dt)
    return html

@app.post("/reports/weekly/send")
def report_weekly_send():
    ok, info = send_report("weekly")
    flash("週次レポートを送信しました。" if ok else f"週次レポート送信に失敗：{info}")
    return redirect(url_for("setting"))

@app.get("/reports/monthly/preview")
def report_monthly_preview():
    title, start_dt, end_dt = _report_range("monthly")
    html = render_report_html(title, start_dt, end_dt)
    return html

@app.post("/reports/monthly/send")
def report_monthly_send():
    ok, info = send_report("monthly")
    flash("月次レポートを送信しました。" if ok else f"月次レポート送信に失敗：{info}")
    return redirect(url_for("setting"))

# ---------- その他ページ -------------------------------------------------------
@app.route("/ocr", methods=["GET", "POST"])
def ocr():
    return render_template("pages/ocr.html")

@app.route("/suppliers")
def suppliers():
    return render_template("pages/suppliers.html")

@app.route("/setting", methods=["GET", "POST"])
def setting():
    s = AppSettings.get()
    if request.method == "POST":
        new_pass = (request.form.get("mail_pass") or "").strip() or s.mail_pass
        s.mail_enabled = request.form.get("mail_enabled") in ("on","1","true")
        s.mail_provider = (request.form.get("mail_provider") or "gmail").strip().lower()
        s.mail_from = (request.form.get("mail_from") or "").strip()
        s.mail_to   = (request.form.get("mail_to") or "").strip()
        s.mail_pass = new_pass
        s.profit_threshold = _to_int(request.form.get("profit_threshold"))
        s.updated_at = datetime.utcnow()
        db.session.commit()
        flash("設定を保存しました。")
        return redirect(url_for("setting"))
    return render_template("pages/setting.html", s=s)

@app.post("/setting/test-mail")
def setting_test_mail():
    s = AppSettings.get()
    subj = "【リサーチナビ】テスト送信"
    html = (f"<h2>テスト送信</h2>"
            f"<p>送信元: {s.mail_from}<br>送信先: {s.mail_to}<br>"
            f"閾値: ¥{s.profit_threshold:,}<br>"
            f"時刻: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}</p>")
    ok, info = send_mail_by_settings(subj, html, "[テスト送信] ResearchNavi")
    flash("テストメールを送信しました。" if ok else f"テスト送信に失敗：{info}")
    return redirect(url_for("setting"))

# ---------- 健康診断 / エラー --------------------------------------------------
@app.route("/healthz")
def healthz():
    return "ok", 200

@app.route("/dbcheck")
def dbcheck():
    try:
        v = db.session.execute(text("SELECT 1")).scalar_one()
        return f"DB OK ({v})"
    except Exception as e:
        return f"DB ERROR: {e}", 500

@app.errorhandler(404)
def _404(e):
    return render_template("errors/404.html"), 404

@app.errorhandler(500)
def _500(e):
    return render_template("errors/500.html"), 500

if __name__ == "__main__":
    # Render は Start Command で waitress を使う想定
    app.run(host="0.0.0.0", port=5000, debug=True)
