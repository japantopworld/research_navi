import os
import csv
import re
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session

# -----------------------------
# Flaskアプリ設定
# -----------------------------
app = Flask(__name__)
app.secret_key = "change-me"  # 本番では安全なキーに変更

# -----------------------------
# データ関連
# -----------------------------
DATA_DIR = os.path.join("research_navi", "data")
USERS_CSV = os.path.join(DATA_DIR, "users.csv")

def ensure_users_csv():
    """users.csvが存在しなければ初期作成"""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(USERS_CSV):
        with open(USERS_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "ユーザー名","ふりがな","生年月日","年齢","電話番号","携帯番号",
                "メールアドレス","部署","紹介者NO","ID","PASS"
            ])

def calc_age(birth_ymd: str) -> str:
    """生年月日から年齢計算"""
    try:
        b = datetime.strptime(birth_ymd, "%Y-%m-%d").date()
        t = datetime.now().date()
        return str(t.year - b.year - ((t.month, t.day) < (b.month, b.day)))
    except Exception:
        return ""

def id_exists(user_id: str) -> bool:
    """IDが既に存在するか確認"""
    if not os.path.exists(USERS_CSV):
        return False
    with open(USERS_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("ID") == user_id:
                return True
    return False

def mmdd_from_birth(birth_ymd: str) -> str:
    """生年月日からMMDD形式を生成"""
    try:
        d = datetime.strptime(birth_ymd, "%Y-%m-%d").date()
        return f"{d.month:02d}{d.day:02d}"
    except Exception:
        return ""

def normalize_ref(raw: str) -> str:
    """紹介者NOの正規化: KA, KB1 → A, B1"""
    if not raw:
        return ""
    s = raw.strip().upper()
    if s.startswith("K"):
        s = s[1:]
    m = re.fullmatch(r"([A-E])([0-9])?", s)
    if not m:
        return ""
    alpha, digit = m.group(1), (m.group(2) or "")
    return f"{alpha}{digit}"

# =========================================================
# ルート定義
# =========================================================

# -----------------------------
# ホーム画面
# -----------------------------
@app.route("/home")
def home():
    return render_template("pages/home.html")

@app.route("/")
def index():
    return redirect(url_for("home"))

# -----------------------------
# サポート関連ページ
# -----------------------------
@app.route("/guide", endpoint="guide")
def page_guide():
    return render_template("support/guide.html")

@app.route("/terms", endpoint="terms")
def page_terms():
    return render_template("support/terms.html")

@app.route("/privacy", endpoint="privacy")
def page_privacy():
    return render_template("support/privacy.html")

@app.route("/report", endpoint="report")
def page_report():
    return render_template("support/report.html")

@app.route("/support", endpoint="support")
def page_support():
    return render_template("support/support.html")

# -----------------------------
# ログイン
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        input_id = request.form.get("username", "").strip()
        input_pass = request.form.get("password", "").strip()

        # 管理者ログイン
        if input_id == "KING121_
