import os, csv, re
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory

# -----------------------------
# Flask app 定義
# -----------------------------
app = Flask(__name__)
app.secret_key = "change-me"  # 本番は安全なキーに変更

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
# ユーザー関連のユーティリティ
# -----------------------------
def ensure_users_csv():
    if not os.path.exists(USERS_CSV):
        with open(USERS_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "ユーザー名","ふりがな","生年月日","年齢","電話番号","携帯番号",
                "メールアドレス","部署","紹介者NO","ID","PASS"
            ])

def id_exists(user_id: str) -> bool:
    if not os.path.exists(USERS_CSV):
        return False
    with open(USERS_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("ID") == user_id:
                return True
    return False

# -----------------------------
# ホーム & 認証
# -----------------------------
@app.route("/")
@app.route("/home")
def home():
    return render_template("pages/home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        input_id = request.form.get("username","").strip()
        input_pass = request.form.get("password","").strip()

        if input_id == "KING1219" and input_pass == "11922960":
            session["logged_in"] = True
            session["user_id"] = "KING1219"
            return redirect(url_for("mypage", user_id="KING1219"))

        ensure_users_csv()
        with open(USERS_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            user = next((row for row in reader if row["ID"] == input_id and row["PASS"] == input_pass), None)

        if user:
            session["logged_in"] = True
            session["user_id"] = user["ID"]
            return redirect(url_for("mypage", user_id=user["ID"]))
        else:
            return render_template("auth/login.html", error="ユーザーIDまたはパスワードが違います")

    return render_template("auth/login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# -----------------------------
# マイページ
# -----------------------------
@app.route("/mypage/<user_id>")
def mypage(user_id):
    if not session.get("logged_in") or session.get("user_id") != user_id:
        return redirect(url_for("login"))

    ensure_users_csv()
    with open(USERS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        user = next((row for row in reader if row["ID"] == user_id), None)

    if not user and user_id == "KING1219":
        user = {"ユーザー名": "小島崇彦","ID": "KING1219","メールアドレス":"","部署":"","紹介者NO":""}

    display_name = user.get("ユーザー名") or user.get("ID") or user_id
    return render_template("pages/mypage.html", user=user, display_name=display_name)

# -----------------------------
# メールボックス機能
# -----------------------------
@app.route("/news", methods=["GET", "POST"])
def news():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    user_id = session.get("user_id")
    tab = request.args.get("tab", "inbox")

    messages = []
    if os.path.exists(SUPPORT_CSV):
        with open(SUPPORT_CSV, newline="", encoding="utf-8") as f:
            all_messages = list(csv.DictReader(f))

        if tab == "inbox":
            messages = [m for m in all_messages if m["宛先"] == user_id]
        elif tab == "sent":
            messages = [m for m in all_messages if m["送信者"] == user_id]

    # 新規作成
    if request.method == "POST" and tab == "compose":
        to = request.form.get("to", "").strip()
        subject = request.form.get("subject", "").strip()
        body = request.form.get("body", "").strip()
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        # 添付ファイル保存
        attachment = ""
        if "attachment" in request.files:
            file = request.files["attachment"]
            if file.filename:
                filepath = os.path.join(UPLOAD_DIR, file.filename)
                file.save(filepath)
                attachment = file.filename

        # ID付与は全体数ベース
        all_count = 0
        if os.path.exists(SUPPORT_CSV):
            with open(SUPPORT_CSV, newline="", encoding="utf-8") as f:
                all_count = len(list(csv.DictReader(f)))

        new_msg = {
            "ID": str(all_count),
            "送信者": user_id,
            "宛先": to,
            "件名": subject,
            "本文": body,
            "添付": attachment,
            "ステータス": "未読",
            "送信日時": now
        }

        file_exists = os.path.exists(SUPPORT_CSV)
        with open(SUPPORT_CSV, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=new_msg.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(new_msg)

        return redirect(url_for("news", tab="sent"))

    return render_template("pages/news.html", tab=tab, messages=messages, user_id=user_id)

@app.route("/news/<int:msg_id>")
def news_detail(msg_id):
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    if not os.path.exists(SUPPORT_CSV):
        return "メッセージが存在しません", 404

    with open(SUPPORT_CSV, newline="", encoding="utf-8") as f:
        messages = list(csv.DictReader(f))

    if msg_id < 0 or msg_id >= len(messages):
        return "メッセージが存在しません", 404

    message = messages[msg_id]

    # 既読処理
    if message["ステータス"] == "未読" and message["宛先"] == session.get("user_id"):
        messages[msg_id]["ステータス"] = "既読"
        with open(SUPPORT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=messages[0].keys())
            writer.writeheader()
            writer.writerows(messages)

    return render_template("pages/news_detail.html", message=message, msg_id=msg_id)

@app.route("/uploads/<filename>")
def download_file(filename):
    return send_from_directory(UPLOAD_DIR, filename, as_attachment=True)

# -----------------------------
# その他ページ（略）
# -----------------------------
@app.route("/guide")
def guide(): return render_template("support/guide.html")
@app.route("/terms")
def terms(): return render_template("support/terms.html")
@app.route("/privacy")
def privacy(): return render_template("support/privacy.html")
@app.route("/report")
def report(): return render_template("support/report.html")
@app.route("/support")
def support(): return render_template("support/support.html")
@app.route("/services")
def services(): return render_template("pages/suppliers.html")
@app.route("/settings")
def settings(): return render_template("pages/setting.html")

@app.route("/healthz")
def healthz(): return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
