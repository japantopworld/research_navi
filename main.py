# main.py — ResearchNavi (SQLite安定版 / WAL+timeout / CSV自動移行)
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
import os, csv, json, smtplib, re, io, zipfile, hashlib, random, math, sqlite3
from email.message import EmailMessage
from collections import defaultdict
from datetime import datetime, date, timedelta

# ---- OCR（任意） ----
try:
    import pytesseract
    from PIL import Image
except Exception:
    pytesseract = None
    Image = None

app = Flask(__name__)
app.secret_key = "researchnavi_secret"

# ---- パス & ストレージ ----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 既存CSV（あれば自動移行）
CSV_PATH   = os.path.join(DATA_DIR, "profit_history.csv")
# 設定・通知（JSONのまま）
SET_PATH   = os.path.join(DATA_DIR, "settings.json")
NOTES_PATH = os.path.join(DATA_DIR, "notes.json")

# SQLite
DB_PATH = os.path.join(DATA_DIR, "app.db")

CSV_HEADERS = [
    "日時","商品名","プラットフォーム","仕入価格","販売価格","送料",
    "追加手数料","手数料率(%)","手数料(円)","利益","利益率(%)"
]

DEFAULT_SETTINGS = {
    "profit_threshold": 8000,
    "mail_enabled": False,
    "mail_provider": "gmail",
    "mail_from": "",
    "mail_to": "",
    "mail_pass": ""
}

# 初期ファイル
if not os.path.exists(SET_PATH):
    with open(SET_PATH, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_SETTINGS, f, ensure_ascii=False, indent=2)
if not os.path.exists(NOTES_PATH):
    with open(NOTES_PATH, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

# ---- テンプレ便利フィルタ ----
def yen(value):
    try: return "¥{:,.0f}".format(float(value))
    except: return str(value)
app.jinja_env.filters["yen"] = yen

# ---- 設定/通知ユーティリティ ----
def load_settings():
    try:
        with open(SET_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return DEFAULT_SETTINGS.copy()

def save_settings(data: dict):
    with open(SET_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def read_notes():
    try:
        with open(NOTES_PATH, "r", encoding="utf-8") as f:
            notes = json.load(f)
            for n in notes:
                if "read" not in n: n["read"] = False
            return notes
    except:
        return []

def write_notes(notes):
    with open(NOTES_PATH, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)

def append_note(title: str, message: str, level: str = "info",
                ntype: str = "text", payload: dict | None = None):
    notes = read_notes()
    notes.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "title": title, "message": message,
        "level": level, "type": ntype, "payload": payload or {},
        "read": False
    })
    write_notes(notes)

# ---- メール送信（Gmailアプリパス対応） ----
def _send_mail_html(settings: dict, subject: str, text_body: str, html_body: str):
    if not settings.get("mail_enabled"):
        return False, "メール通知は無効です。"
    provider = (settings.get("mail_provider") or "gmail").lower()
    sender   = (settings.get("mail_from") or "").strip()
    to_field = (settings.get("mail_to") or "").strip()
    app_pass = (settings.get("mail_pass") or "").strip()
    if not (sender and to_field and app_pass):
        return False, "送信に必要な設定（FROM/TO/PASS）が未入力です。"
    recipients = [x.strip() for x in to_field.split(",") if x.strip()]
    if not recipients:
        return False, "送信先メール（MAIL_TO）が空です。"
    if provider != "gmail":
        return False, f"未対応のプロバイダです: {provider}"
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = ", ".join(recipients)
        msg.set_content(text_body)
        msg.add_alternative(html_body, subtype="html")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as smtp:
            smtp.login(sender, app_pass)
            smtp.send_message(msg)
        return True, f"送信完了: {len(recipients)}件"
    except Exception as e:
        return False, f"送信失敗: {e}"

def build_profit_mail_payload(name, platform, price, cost, ship, fee_calc, profit_val, margin, threshold):
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    subject = f"[リサーチナビ] 利益通知 {yen(profit_val)}（{name}）"
    text_body = (
        f"商品名: {name}\nプラットフォーム: {platform}\n利益: {yen(profit_val)}（利益率 {margin}%）\n"
        f"販売: {yen(price)} / 仕入: {yen(cost)} / 送料: {yen(ship)} / 手数料合計: {yen(fee_calc)}\n"
        f"閾値: {yen(threshold)}\n日時: {now}\n"
    )
    html_body = render_template("email/profit_notice.html",
        name=name, platform=platform, price=price, cost=cost, ship=ship,
        fee_calc=fee_calc, profit_val=profit_val, margin=margin,
        threshold=threshold, now=now)
    return subject, text_body, html_body

# ---- SQLite（WAL+timeout セットアップ & CSV移行） ----
def db_connect():
    # timeout: ロック時の待ち秒数（書込み集中時のエラー回避）
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10.0)
    conn.row_factory = sqlite3.Row
    # 重要PRAGMA（接続毎に適用）
    conn.execute("PRAGMA journal_mode=WAL;")     # 並列読取に強い
    conn.execute("PRAGMA synchronous=NORMAL;")   # 性能と安全のバランス
    conn.execute("PRAGMA busy_timeout=8000;")    # ロック時に最大8秒待つ
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def db_setup_and_migrate():
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS profit_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dt TEXT NOT NULL,
            name TEXT NOT NULL,
            platform TEXT NOT NULL,
            cost REAL NOT NULL,
            price REAL NOT NULL,
            ship REAL NOT NULL,
            extra_fee REAL NOT NULL,
            fee_rate REAL NOT NULL,
            fee_calc REAL NOT NULL,
            profit REAL NOT NULL,
            margin REAL NOT NULL
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_profit_dt ON profit_history(dt)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_profit_name ON profit_history(name)")
    conn.commit()

    # テーブルが空 & CSV が存在 → 自動移行
    cur.execute("SELECT COUNT(*) AS c FROM profit_history")
    empty = (cur.fetchone()["c"] == 0)
    if empty and os.path.exists(CSV_PATH):
        try:
            with open(CSV_PATH, newline="", encoding="utf-8") as f:
                rdr = csv.DictReader(f)
                rows = [r for r in rdr if r.get("商品名")]
            for r in rows:
                def fnum(x):
                    try: return float(str(x).replace(",",""))
                    except: return 0.0
                dt = r.get("日時") or datetime.now().strftime("%Y-%m-%d %H:%M")
                cur.execute("""
                    INSERT INTO profit_history
                    (dt,name,platform,cost,price,ship,extra_fee,fee_rate,fee_calc,profit,margin)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    dt,
                    r.get("商品名") or "（名称未設定）",
                    r.get("プラットフォーム") or "メルカリ",
                    fnum(r.get("仕入価格")), fnum(r.get("販売価格")), fnum(r.get("送料")),
                    fnum(r.get("追加手数料")), fnum(r.get("手数料率(%)")), fnum(r.get("手数料(円)")),
                    fnum(r.get("利益")), fnum(r.get("利益率(%)")),
                ))
            conn.commit()
            append_note("データ移行", f"CSV から {len(rows)} 件をSQLiteに取り込みました。", "success")
        except Exception as e:
            append_note("データ移行失敗", f"{e}", "warning")
    conn.close()

db_setup_and_migrate()

def db_insert_profit(dt, name, platform, cost, price, ship, extra_fee, fee_rate, fee_calc, profit_val, margin):
    conn = db_connect()
    conn.execute("""
        INSERT INTO profit_history
        (dt,name,platform,cost,price,ship,extra_fee,fee_rate,fee_calc,profit,margin)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (dt,name,platform,cost,price,ship,extra_fee,fee_rate,fee_calc,profit_val,margin))
    conn.commit()
    conn.close()

def db_fetch_history(start=None, end=None, platforms=None, min_profit=None, keyword=None, order_desc=True):
    sql = "SELECT dt,name,platform,cost,price,ship,extra_fee,fee_rate,fee_calc,profit,margin FROM profit_history WHERE 1=1"
    p = []
    if start:
        sql += " AND dt >= ?"; p.append(start)
    if end:
        sql += " AND dt <= ?"; p.append(end)
    if platforms:
        qs = ",".join(["?"]*len(platforms))
        sql += f" AND platform IN ({qs})"; p += platforms
    if min_profit is not None:
        sql += " AND profit >= ?"; p.append(min_profit)
    if keyword:
        sql += " AND name LIKE ?"; p.append(f"%{keyword}%")
    sql += " ORDER BY dt " + ("DESC" if order_desc else "ASC")
    conn = db_connect()
    rows = [dict(r) for r in conn.execute(sql, p).fetchall()]
    conn.close()
    # テンプレ互換のキーに整形
    return [{
        "日時": r["dt"],
        "商品名": r["name"],
        "プラットフォーム": r["platform"],
        "仕入価格": r["cost"],
        "販売価格": r["price"],
        "送料": r["ship"],
        "追加手数料": r["extra_fee"],
        "手数料率(%)": r["fee_rate"],
        "手数料(円)": r["fee_calc"],
        "利益": r["profit"],
        "利益率(%)": r["margin"],
    } for r in rows]

def db_fetch_all_for_export(start=None, end=None, platforms=None, min_profit=None, keyword=None):
    return db_fetch_history(start, end, platforms, min_profit, keyword, order_desc=False)

# =========================================================
# ルーティング
# =========================================================

@app.route("/")
def home():
    return render_template("pages/home.html")

@app.route("/search")
def search():
    return render_template("pages/search.html")

FEE_PRESETS = [("メルカリ",10.0), ("Amazon",15.0), ("Yahoo!",8.0)]

@app.route("/profit", methods=["GET","POST"])
def profit():
    if request.method == "POST":
        name=(request.form.get("name") or "").strip() or "（名称未設定）"
        platform=request.form.get("platform") or "メルカリ"
        cost=float(request.form.get("cost") or 0)
        price=float(request.form.get("price") or 0)
        ship=float(request.form.get("ship") or 0)
        extra_fee=float(request.form.get("extra_fee") or 0)
        fee_rate=float(request.form.get("fee_rate") or 10)
        fee_calc=round(price*(fee_rate/100.0)+extra_fee,2)
        profit_val=round(price-cost-ship-fee_calc,2)
        margin=round((profit_val/price*100.0),2) if price>0 else 0.0

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        db_insert_profit(now_str, name, platform, cost, price, ship, extra_fee, fee_rate, fee_calc, profit_val, margin)

        settings=load_settings()
        threshold=float(settings.get("profit_threshold",8000))
        if profit_val>=threshold:
            payload={"name":name,"platform":platform,"price":price,"cost":cost,"ship":ship,
                     "fee_calc":fee_calc,"profit_val":profit_val,"margin":margin,"threshold":threshold}
            append_note("利益通知", f"{name} が {yen(profit_val)} の黒字（閾値 {yen(threshold)} 以上）",
                        "success", ntype="profit", payload=payload)
            sub,t,h=build_profit_mail_payload(**payload)
            ok,msg=_send_mail_html(settings,sub,t,h)
            append_note("メール送信", msg, "success" if ok else "warning")
            flash(("📧 " if ok else "⚠️ ")+msg)

        flash(f"保存しました：{name} / 利益 {yen(profit_val)}（利益率 {margin}%）")
        return redirect(url_for("history"))

    initial={"name":request.args.get("name",""),"platform":request.args.get("platform","メルカリ"),
             "cost":request.args.get("cost","0"),"price":request.args.get("price","0"),
             "ship":request.args.get("ship","0"),"extra_fee":request.args.get("extra_fee","0"),
             "fee_rate":request.args.get("fee_rate","10")}
    return render_template("pages/profit.html", fee_presets=FEE_PRESETS, initial=initial, settings=load_settings())

@app.route("/history")
def history():
    rows = db_fetch_history()  # 最新順
    return render_template("pages/history.html", rows=rows)

# ---- 履歴エクスポート（フィルタ付き） ----
@app.route("/history/export")
def history_export():
    start_s=request.args.get("start"); end_s=request.args.get("end")
    plats_s=request.args.get("platform","")
    min_profit_s=request.args.get("min_profit","")
    keyword=(request.args.get("keyword") or "").strip()

    start = f"{start_s} 00:00" if start_s else None
    end   = f"{end_s} 23:59" if end_s else None
    platforms=[p for p in plats_s.split(",") if p]
    try: min_pf=float(min_profit_s) if min_profit_s!='' else None
    except: min_pf=None

    rows = db_fetch_all_for_export(start, end, platforms or None, min_pf, keyword or None)

    output=io.StringIO()
    w=csv.DictWriter(output, fieldnames=CSV_HEADERS)
    w.writeheader()
    for r in rows: w.writerow(r)
    mem=io.BytesIO()
    mem.write('\ufeff'.encode('utf-8'))
    mem.write(output.getvalue().encode('utf-8'))
    mem.seek(0)
    fn = f"history_{(start_s or 'all')}_{(end_s or 'all')}.csv"
    return send_file(mem, as_attachment=True, download_name=fn, mimetype="text/csv")

# ---- ランキング（期間＋スパークライン） ----
@app.route("/ranking")
def ranking():
    metric = request.args.get("metric", "avg_profit")
    try: min_count = int(request.args.get("min", 1))
    except: min_count = 1
    start_s = request.args.get("start", "")
    end_s   = request.args.get("end", "")

    today = date.today()
    def month_range(target: date):
        first = target.replace(day=1)
        next_m = (first.replace(day=28) + timedelta(days=4)).replace(day=1)
        last = next_m - timedelta(days=1)
        return first, last

    if not start_s and not end_s:
        s_d, e_d = month_range(today)
    else:
        try: s_d = datetime.strptime(start_s, "%Y-%m-%d").date()
        except: s_d = date(2000,1,1)
        try: e_d = datetime.strptime(end_s, "%Y-%m-%d").date()
        except: e_d = date(2999,12,31)

    start = f"{s_d} 00:00"; end = f"{e_d} 23:59"
    src = db_fetch_all_for_export(start, end, None, None, None)  # 昇順で扱う

    # 集計
    agg = defaultdict(lambda: {"count":0, "profits":[], "margins":[], "series": []})
    def to_f(x):
        try: return float(x)
        except: return 0.0

    # 時系列（昇順）に
    src.sort(key=lambda r: r["日時"])
    for r in src:
        name = (r.get("商品名") or "").strip() or "（名称未設定）"
        p = to_f(r.get("利益")); m = to_f(r.get("利益率(%)"))
        a = agg[name]
        a["count"] += 1
        a["profits"].append(p)
        a["margins"].append(m)
        a["series"].append(p)

    def thin(series, max_points=24):
        if len(series) <= max_points: return series
        step = len(series) / max_points
        return [ series[math.floor(i*step)] for i in range(max_points) ]

    rows = []
    for name, a in agg.items():
        if a["count"] < min_count: continue
        count = a["count"]; s = sum(a["profits"]); avg = s/count if count else 0
        avgm = sum(a["margins"])/count if count else 0; mx = max(a["profits"]) if a["profits"] else 0
        rows.append({"商品名":name,"件数":count,"平均利益":round(avg),"平均利益率":round(avgm,1),
                     "最高利益":round(mx),"合計利益":round(s),"series": thin(a["series"])})

    key_map = {"avg_profit":("平均利益",True),"avg_margin":("平均利益率",True),
               "max_profit":("最高利益",True),"total_profit":("合計利益",True)}
    key,desc = key_map.get(metric, ("平均利益", True))
    rows.sort(key=lambda x: (x.get(key,0), x.get("件数",0)), reverse=desc)

    return render_template("pages/ranking.html",
                           metric=metric, min_count=min_count,
                           start=s_d, end=e_d,
                           rows=rows, top3=rows[:3], rest=rows[3:10])

# ---- 通知 ----
@app.route("/notifications")
def notifications():
    raw = read_notes()
    annotated = [{"__idx": i, **n} for i, n in enumerate(raw)]
    annotated.sort(key=lambda n: n.get("time",""), reverse=True)
    threshold=float(load_settings().get("profit_threshold",8000))
    unread_count = sum(1 for n in raw if not n.get("read"))
    return render_template("pages/notifications.html", notes=annotated, threshold=threshold, unread_count=unread_count)

@app.route("/notifications/resend/<int:index>", methods=["POST"])
def notifications_resend(index: int):
    notes = read_notes()
    if index < 0 or index >= len(notes):
        flash("対象の通知が見つかりません。"); return redirect(url_for("notifications"))
    note = notes[index]
    if note.get("type") != "profit":
        flash("この通知は再送できません。"); return redirect(url_for("notifications"))
    payload = note.get("payload") or {}
    sub, t, h = build_profit_mail_payload(**payload)
    ok, msg = _send_mail_html(load_settings(), sub, t, h)
    append_note("メール再送", msg, "success" if ok else "warning")
    flash(("📧 " if ok else "⚠️ ") + msg)
    return redirect(url_for("notifications"))

@app.route("/notifications/mark/<int:index>", methods=["POST"])
def notifications_mark(index:int):
    notes=read_notes()
    if 0<=index<len(notes):
        notes[index]["read"] = bool(int(request.form.get("read","1")))
        write_notes(notes)
    return redirect(url_for("notifications"))

@app.route("/notifications/mark_all", methods=["POST"])
def notifications_mark_all():
    notes=read_notes()
    for n in notes: n["read"]=True
    write_notes(notes)
    return redirect(url_for("notifications"))

# ---- 設定 ----
@app.route("/setting", methods=["GET","POST"])
def setting():
    settings = load_settings()
    if request.method == "POST":
        try:
            settings["profit_threshold"] = float(request.form.get("profit_threshold", settings["profit_threshold"]))
        except: pass
        settings["mail_enabled"]  = True if request.form.get("mail_enabled") else False
        settings["mail_provider"] = request.form.get("mail_provider", settings.get("mail_provider","gmail"))
        settings["mail_from"]     = request.form.get("mail_from", settings.get("mail_from",""))
        settings["mail_to"]       = request.form.get("mail_to", settings.get("mail_to",""))
        pw = (request.form.get("mail_pass") or "").strip()
        if pw: settings["mail_pass"] = pw
        save_settings(settings)
        flash("設定を保存しました。")
        return redirect(url_for("setting"))
    return render_template("pages/setting.html", settings=settings)

# ---- OCR ----
PRICE_PAT=re.compile(r'(?:¥|JPY|￥)?\s*([0-9]{1,3}(?:[,，][0-9]{3})+|[0-9]+)')
RATE_PAT =re.compile(r'([0-9]{1,2}(?:\.[0-9])?)\s*%')
def _to_int(s): return int(re.sub(r'[^0-9]','',str(s)) or 0) if s is not None else 0
def guess_fields(text):
    prices=[_to_int(m.group(1)) for m in PRICE_PAT.finditer(text)]
    m=RATE_PAT.search(text); rate=float(m.group(1)) if m else None
    prices_sorted=sorted([p for p in prices if p>0], reverse=True)
    price=prices_sorted[0] if prices_sorted else 0
    cost=prices_sorted[1] if len(prices_sorted)>=2 else 0
    ship=0
    if '送料' in text or '配送料' in text:
        smalls=sorted([p for p in prices if 0<p<=1000]); ship=smalls[-1] if smalls else 0
    fee_rate=rate if rate is not None else 10.0
    lines=[ln.strip() for ln in text.splitlines() if ln.strip()]
    name=lines[0][:60] if lines else "（名称未設定）"
    return {"name":name,"platform":"メルカリ","price":price,"cost":cost,"ship":ship,"extra_fee":0,"fee_rate":fee_rate}

@app.route("/ocr", methods=["GET","POST"])
def ocr():
    ocr_enabled, result, raw_text, err = bool(pytesseract and Image), None, None, None
    if request.method=="POST":
        file=request.files.get("image")
        if not file or file.filename=="": err="画像ファイルを選択してください。"
        elif not ocr_enabled: err="OCRエンジンが未導入です。Tesseract と pytesseract をインストールしてください。"
        else:
            tmp=os.path.join(UPLOAD_DIR, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
            file.save(tmp)
            try:
                img=Image.open(tmp); text=pytesseract.image_to_string(img, lang="jpn+eng")
                raw_text=text; result=guess_fields(text)
            except Exception as e:
                err=f"OCR失敗: {e}"
    return render_template("pages/ocr.html", ocr_enabled=ocr_enabled, ocr_result=result, raw_text=raw_text, error=err)

# ---- 仕入れ先 ----
@app.route("/suppliers")
def suppliers():
    return render_template("pages/suppliers.html")

# ---- モックAPI（検索）----
def mock_product(asin: str | None = None, jan: str | None = None):
    seed=(asin or jan or "X").encode("utf-8"); h=int(hashlib.sha256(seed).hexdigest(),16); random.seed(h)
    base=random.randint(1500,58000)
    return {
        "title": f"Sample Product {(asin or jan or '')[:6]}",
        "image": "https://via.placeholder.com/480x480.png?text=ResearchNavi",
        "category": random.choice(["家電・カメラ","ゲーム","おもちゃ","ホーム&キッチン","パソコン"]),
        "asin": asin or "", "jan": jan or "",
        "amazon_price": base, "new_price": base-random.randint(0,2000),
        "used_price": max(500, base-random.randint(2000,10000)), "sales_rank": random.randint(50,50000)
    }

@app.route("/api/product")
def api_product():
    asin=(request.args.get("asin") or "").strip().upper()
    jan =(request.args.get("jan") or "").strip()
    if not asin and not jan:
        return jsonify({"ok":False,"error":"asin か jan を指定してください。"}),400
    provider=(os.getenv("RN_PRODUCT_PROVIDER") or "mock").lower()
    try:
        if provider=="mock":
            return jsonify({"ok":True,"provider":"mock","data":mock_product(asin or None, jan or None)})
        else:
            return jsonify({"ok":False,"error":f"未対応のprovider: {provider}"}),500
    except Exception as e:
        return jsonify({"ok":False,"error":f"取得失敗: {e}"}),500

# ---- 追加のエクスポート便利機能 ----
@app.route("/export/csv")
def export_csv():
    rows = db_fetch_all_for_export()
    output=io.StringIO()
    w=csv.DictWriter(output, fieldnames=CSV_HEADERS)
    w.writeheader()
    for r in rows: w.writerow(r)
    mem=io.BytesIO()
    mem.write('\ufeff'.encode('utf-8'))
    mem.write(output.getvalue().encode('utf-8'))
    mem.seek(0)
    return send_file(mem, as_attachment=True,
                     download_name=f"profit_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                     mimetype="text/csv")

@app.route("/export/backup.zip")
def export_backup():
    mem=io.BytesIO()
    with zipfile.ZipFile(mem,"w",zipfile.ZIP_DEFLATED) as z:
        # DB→CSV化して同梱
        rows = db_fetch_all_for_export()
        csv_buf=io.StringIO()
        w=csv.DictWriter(csv_buf, fieldnames=CSV_HEADERS)
        w.writeheader()
        for r in rows: w.writerow(r)
        z.writestr("profit_history.csv", '\ufeff'+csv_buf.getvalue())
        with open(SET_PATH,"r",encoding="utf-8") as f: z.writestr("settings.json", f.read())
        with open(NOTES_PATH,"r",encoding="utf-8") as f: z.writestr("notes.json", f.read())
    mem.seek(0)
    return send_file(mem, as_attachment=True,
                     download_name=f"research_navi_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                     mimetype="application/zip")

# ---- エラー ----
@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("errors/500.html"), 500

if __name__ == "__main__":
    app.run(debug=True)
