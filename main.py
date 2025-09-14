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
# ルート: ホーム -> ログインへ
# -----------------------------
@app.route("/")
def home():
    return redirect(url_for("login"))

# -----------------------------
# 新規登録
# -----------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    ensure_users_csv()
    errors = []
    form = {}

    if request.method == "POST":
        form = request.form.to_dict()

        name = form.get("name", "").strip()
        kana = form.get("kana", "").strip()
        birth = form.get("birth", "").strip()
        branch = form.get("branch", "").strip()
        phone = form.get("phone", "").strip()
        mobile = form.get("mobile", "").strip()
        email = form.get("email", "").strip()
        dept = form.get("dept", "").strip()
        ref_raw = form.get("ref_raw", "").strip()
        ref_no = form.get("ref_no", "").strip()
        user_id = form.get("user_id", "").strip()
        password = form.get("password", "")
        password2 = form.get("password2", "")

        # 入力チェック
        if not name: errors.append("氏名は必須です")
        if not kana: errors.append("ふりがなは必須です")
        if not birth: errors.append("生年月日は必須です")
        if not ref_no: errors.append("紹介者NOの正規化ができません")
        if not user_id: errors.append("ユーザーIDが生成されていません")
        if not password: errors.append("パスワードは必須です")
        if password != password2: errors.append("パスワードが一致しません")

        # 既存IDチェック
        if os.path.exists(USERS_CSV):
            with open(USERS_CSV, newline="", encoding="utf-8") as f:
                users = list(csv.DictReader(f))
                if any(u["ID"] == user_id for u in users):
                    errors.append("このユーザーIDはすでに登録されています")

        if not errors:
            # CSV保存
            with open(USERS_CSV, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    name, kana, birth, "", phone, mobile,
                    email, dept, ref_no, user_id, password
                ])
            return redirect(url_for("login"))

    return render_template("auth/register.html", errors=errors, form=form)

# -----------------------------
# ログイン
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
# メールボックス
# -----------------------------
@app.route("/news", methods=["GET", "POST"])
def news():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    user_id = session.get("user_id")
    tab = request.args.get("tab", "inbox")
    query = request.args.get("q", "").strip()

    # 返信用パラメータ
    reply_to = request.args.get("reply_to", "")
    reply_subject = request.args.get("subject", "")

    # メッセージ一覧
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
        if messages:
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
            if os.path.exists(SUPPORT_CSV):
                os.remove(SUPPORT_CSV)
        return redirect(url_for("news", tab=tab))

    # ✉ 新規送信
    if request.method == "POST" and tab == "compose":
        to = request.form.get("to", "").strip()
        subject = request.form.get("subject", "").strip()
        body = request.form.get("body", "").strip()
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        # 添付
        file_path = ""
        file = request.files.get("attach")
        if file and file.filename:
            filename = f"{datetime.now().timestamp()}_{file.filename}"  # ←修正済
            save_path = os.path.join(UPLOAD_DIR, filename)
            file.save(save_path)
            file_path = filename

        # 宛先（@部署名 で一斉送信）
        recipients = []
        if to.startswith("@"):
            dept = to[1:]
            if os.path.exists(USERS_CSV):
                with open(USERS_CSV, newline="", encoding="utf-8") as f:
                    users = list(csv.DictReader(f))
                    recipients = [u["ID"] for u in users if u["部署"] == dept]
        else:
            recipients = [to]

        # 送信
        for r in recipients:
            new_msg = {
                "ID": str(uuid.uuid4()),
                "送信者": user_id,
                "宛先": r,
                "件名": subject,
                "本文": body,
                "添付": file_path,
                "ステータス": "未読",
                "送信日時": now
            }
            with open(SUPPORT_CSV, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=new_msg.keys())
                if f.tell() == 0:
                    writer.writeheader()
                writer.writerow(new_msg)

        return redirect(url_for("news", tab="sent"))

    # 未読件数
    unread_count = len([m for m in inbox if m["ステータス"] == "未読"])

    return render_template("pages/news.html",
                           tab=tab, inbox=inbox, sent=sent,
                           user_id=user_id, request=request,
                           reply_to=reply_to, reply_subject=reply_subject,
                           unread_count=unread_count)

# -----------------------------
# メッセージ詳細
# -----------------------------
@app.route("/news/<msg_id>")
def news_detail(msg_id):
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    if not os.path.exists(SUPPORT_CSV):
        return "メッセージが存在しません", 404

    with open(SUPPORT_CSV, newline="", encoding="utf-8") as f:
        messages = list(csv.DictReader(f))

    msg = next((m for m in messages if m["ID"] == msg_id), None)
    if not msg:
        return "メッセージが存在しません", 404

    # 既読処理
    if msg["ステータス"] == "未読" and msg["宛先"] == session["user_id"]:
        msg["ステータス"] = "既読"
        with open(SUPPORT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=messages[0].keys())
            writer.writeheader()
            writer.writerows(messages)

    return render_template("pages/news_detail.html", message=msg)

# -----------------------------
# 添付ファイル配信
# -----------------------------
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)
