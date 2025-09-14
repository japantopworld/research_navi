import os, csv, re, uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory

# -----------------------------
# Flask app
# -----------------------------
app = Flask(__name__)
app.secret_key = "change-me"

# -----------------------------
# データ関連
# -----------------------------
DATA_DIR = os.path.join("research_navi", "data")
UPLOAD_DIR = os.path.join("research_navi", "uploads")
USERS_CSV = os.path.join(DATA_DIR, "users.csv")
SUPPORT_CSV = os.path.join(DATA_DIR, "support.csv")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# -----------------------------
# ユーザーCSV初期化
# -----------------------------
def ensure_users_csv():
    if not os.path.exists(USERS_CSV):
        with open(USERS_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "ユーザー名","ふりがな","生年月日","年齢","電話番号","携帯番号",
                "メールアドレス","部署","紹介者NO","ID","PASS"
            ])

# -----------------------------
# 新規登録
# -----------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    ensure_users_csv()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        furigana = request.form.get("furigana", "").strip()
        birth = request.form.get("birth", "").strip()
        age = request.form.get("age", "").strip()
        tel = request.form.get("tel", "").strip()
        mobile = request.form.get("mobile", "").strip()
        email = request.form.get("email", "").strip()
        dept = request.form.get("dept", "").strip()
        refno = request.form.get("refno", "").strip()
        user_id = request.form.get("user_id", "").strip()
        password = request.form.get("password", "").strip()

        with open(USERS_CSV, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([name, furigana, birth, age, tel, mobile,
                             email, dept, refno, user_id, password])

        return redirect(url_for("login"))

    return render_template("auth/register.html")

# -----------------------------
# ログイン（仮置き）
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    ensure_users_csv()
    if request.method == "POST":
        user_id = request.form.get("user_id")
        password = request.form.get("password")

        with open(USERS_CSV, newline="", encoding="utf-8") as f:
            users = list(csv.DictReader(f))

        for u in users:
            if u["ID"] == user_id and u["PASS"] == password:
                session["logged_in"] = True
                session["user_id"] = user_id
                return redirect(url_for("news"))

        return "ログイン失敗"

    return render_template("auth/login.html")

# -----------------------------
# メールボックス（ここまでの最新版）
# -----------------------------
@app.route("/news", methods=["GET", "POST"])
def news():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    user_id = session.get("user_id")
    tab = request.args.get("tab", "inbox")
    query = request.args.get("q", "").strip()

    reply_to = request.args.get("reply_to", "")
    reply_subject = request.args.get("subject", "")

    messages = []
    if os.path.exists(SUPPORT_CSV):
        with open(SUPPORT_CSV, newline="", encoding="utf-8") as f:
            messages = list(csv.DictReader(f))

    inbox = [m for m in messages if m["宛先"] == user_id]
    sent = [m for m in messages if m["送信者"] == user_id]

    # 🔍 検索
    if query:
        if tab == "inbox":
            inbox = [m for m in inbox if query in m["件名"] or query in m["本文"]]
        elif tab == "sent":
            sent = [m for m in sent if query in m["件名"] or query in m["本文"]]

    # ✅ 一括既読
    if request.method == "POST" and request.form.get("action") == "mark_read":
        ids = request.form.getlist("msg_ids")
        for m in messages:
            if m["ID"] in ids and m["宛先"] == user_id:
                m["ステータス"] = "既読"
        with open(SUPPORT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=messages[0].keys())
            writer.writeheader()
            writer.writerows(messages)
        return redirect(url_for("news", tab="inbox"))

    # 🗑️ 削除
    if request.method == "POST" and request.form.get("action") == "delete":
        ids = request.form.getlist("msg_ids")
        messages = [m for m in messages if m["ID"] not in ids]
        if messages:
            with open(SUPPORT_CSV, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=messages[0].keys())
                writer.writeheader()
                writer.writerows(messages)
        else:
            os.remove(SUPPORT_CSV)
        return redirect(url_for("news", tab=tab))

    # ✉ 新規送信
    if request.method == "POST" and tab == "compose":
        to = request.form.get("to", "").strip()
        subject = request.form.get("subject", "").strip()
        body = request.form.get("body", "").strip()
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        file_path = ""
        file = request.files.get("attach")
        if file and file.filename:
            filename = f"{datetime.now(
