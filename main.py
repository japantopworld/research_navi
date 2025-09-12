import os, csv, re
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session

# -----------------------------
# Flask app 定義
# -----------------------------
app = Flask(__name__)
app.secret_key = "change-me"  # セッション用(本番は安全なキーに変更)

# -----------------------------
# データ関連
# -----------------------------
DATA_DIR = os.path.join("research_navi", "data")
USERS_CSV = os.path.join(DATA_DIR, "users.csv")

def ensure_users_csv():
    """users.csv が存在しなければ作成"""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(USERS_CSV):
        with open(USERS_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "ユーザー名","ふりがな","生年月日","年齢","電話番号","携帯番号",
                "メールアドレス","部署","紹介者NO","ID","PASS"
            ])

def calc_age(birth_ymd: str) -> str:
    try:
        b = datetime.strptime(birth_ymd, "%Y-%m-%d").date()
        t = datetime.now().date()
        return str(t.year - b.year - ((t.month, t.day) < (b.month, b.day)))
    except Exception:
        return ""

def id_exists(user_id: str) -> bool:
    if not os.path.exists(USERS_CSV):
        return False
    with open(USERS_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("ID") == user_id:
                return True
    return False

def mmdd_from_birth(birth_ymd: str) -> str:
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

# -----------------------------
# ルート定義
# -----------------------------

# "/" は常にホーム（未ログイン画面）
@app.route("/")
def index():
    return render_template("pages/home.html")

# ログイン
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        input_id = request.form.get("username","").strip()
        input_pass = request.form.get("password","").strip()

        # 管理者
        if input_id == "KING1219" and input_pass == "11922960":
            session["logged_in"] = True
            session["user_id"] = "KING1219"
            return redirect(url_for("mypage", user_id="KING1219"))

        # 通常ユーザー
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

# 登録
@app.route("/register", methods=["GET", "POST"])
def register():
    ensure_users_csv()
    if request.method == "POST":
        name = request.form.get("name","").strip()
        kana = request.form.get("kana","").strip()
        birth = request.form.get("birth","").strip()
        branch = request.form.get("branch","A").strip()
        phone = request.form.get("phone","").strip()
        mobile = request.form.get("mobile","").strip()
        email = request.form.get("email","").strip()
        dept = request.form.get("dept","").strip()

        ref_raw = request.form.get("ref_raw","").strip()
        ref_norm = normalize_ref(ref_raw)

        password = request.form.get("password","")
        password2 = request.form.get("password2","")

        mmdd = mmdd_from_birth(birth)
        user_id = f"{ref_norm}{mmdd}{branch}" if ref_norm and mmdd and branch else ""

        errors = []
        if not name: errors.append("氏名は必須です。")
        if not kana: errors.append("ふりがなは必須です。")
        if not birth: errors.append("生年月日は必須です。")
        if not mmdd: errors.append("生年月日からMMDDが生成できません。")
        if branch not in list("ABCDE"): errors.append("枝は A〜E を選択してください。")
        if not ref_norm: errors.append("紹介者NOの形式が不正です。")
        if not user_id: errors.append("ユーザーIDの生成に失敗しました。")
        if user_id and id_exists(user_id): errors.append("このユーザーIDはすでに登録されています。")
        if not password or len(password) < 6: errors.append("パスワードは6文字以上で入力してください。")
        if password != password2: errors.append("確認用パスワードが一致しません。")

        if errors:
            form = dict(request.form)
            form["ref_no"] = ref_norm
            form["user_id"] = user_id
            return render_template("auth/register.html", errors=errors, form=form)

        age = calc_age(birth)
        with open(USERS_CSV, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                name, kana, birth, age, phone, mobile,
                email, dept, ref_norm, user_id, password
            ])
        return redirect(url_for("login"))

    return render_template("auth/register.html", form={})

# マイページ
@app.route("/mypage/<user_id>")
def mypage(user_id):
    if not session.get("logged_in") or session.get("user_id") != user_id:
        return redirect(url_for("login"))

    ensure_users_csv()
    with open(USERS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        user = next((row for row in reader if row["ID"] == user_id), None)

    if not user and user_id == "KING1219":
        user = {
            "ユーザー名": "小島崇彦",
            "ID": "KING1219",
            "メールアドレス": "",
            "部署": "",
            "紹介者NO": "",
        }

    if not user:
        return "ユーザーが見つかりません", 404

    display_name = user.get("ユーザー名") or user.get("ID") or user_id
    return render_template("pages/mypage.html", user=user, display_name=display_name)

# ログアウト
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# -----------------------------
# サポート関連ページ
# -----------------------------
@app.route("/guide")
def guide():
    return render_template("support/guide.html")

@app.route("/terms")
def terms():
    return render_template("support/terms.html")

@app.route("/privacy")
def privacy():
    return render_template("support/privacy.html")

@app.route("/report")
def report():
    return render_template("support/report.html")

@app.route("/support")
def support():
    return render_template("support/support.html")

# -----------------------------
# その他ページ
# -----------------------------
@app.route("/services")
def services():
    return render_template("pages/suppliers.html")

@app.route("/news")
def news():
    return render_template("pages/guide.html")

@app.route("/settings")
def settings():
    return render_template("pages/setting.html")

# -----------------------------
# Health check
# -----------------------------
@app.route("/healthz")
def healthz():
    return "OK", 200

# -----------------------------
# Render 環境対応
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
