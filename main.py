import os, csv, re
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session

# -----------------------------
# Flask アプリ定義
# -----------------------------
app = Flask(__name__)
app.secret_key = "change-me"  # セッション用（必要なら安全なキーに変更）

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
    """紹介者NOの正規化: KA, KB1 など → A, B1"""
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
@app.route("/")
def index():
    return render_template("pages/home.html")

# /login と /login/ の両方に対応
@app.route("/login", methods=["GET", "POST"])
@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        input_id = request.form.get("username","").strip()
        input_pass = request.form.get("password","").strip()

        # --- 管理者アカウント（直書き） ---
        if input_id == "KING1219" and input_pass == "11922960":
            session["logged_in"] = True
            session["user_id"] = "KING1219"
            return redirect(url_for("mypage", user_id="KING1219"))

        # --- 通常の users.csv 認証 ---
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

# /register と /register/ の両方に対応
@app.route("/register", methods=["GET", "POST"])
@app.route("/register/", methods=["GET", "POST"])
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
        if not ref_norm: errors.append("紹介者NOの形式が不正です（例: KA, KB1）。")
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

# マイページルート
@app.route("/mypage/<user_id>")
def mypage(user_id):
    if not session.get("logged_in") or session.get("user_id") != user_id:
        return redirect(url_for("login"))

    ensure_users_csv()
    with open(USERS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        user = next((row for row in reader if row["ID"] == user_id), None)

    # 管理者（KING1219）はCSVに無くてもOK＋氏名は「小島崇彦」に固定
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

# プロフィール編集ルート
@app.route("/mypage_edit/<user_id>", methods=["GET", "POST"])
def mypage_edit(user_id):
    if not session.get("logged_in") or session.get("user_id") != user_id:
        return redirect(url_for("login"))

    ensure_users_csv()
    users = []
    target_user = None

    with open(USERS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            users.append(row)
            if row["ID"] == user_id:
                target_user = row

    # 👇 管理者（KING1219）はCSVに無くてもOK
    if not target_user and user_id == "KING1219":
        target_user = {
            "ユーザー名": "小島崇彦",
            "ふりがな": "",
            "メールアドレス": "",
            "部署": "",
            "電話番号": "",
            "携帯番号": "",
            "紹介者NO": "",
            "ID": "KING1219",
            "PASS": "11922960"
        }

    if not target_user:
        return "ユーザーが見つかりません", 404

    if request.method == "POST":
        target_user["ユーザー名"] = request.form.get("name", target_user["ユーザー名"])
        target_user["ふりがな"] = request.form.get("kana", target_user["ふりがな"])
        target_user["メールアドレス"] = request.form.get("email", target_user["メールアドレス"])
        target_user["部署"] = request.form.get("dept", target_user["部署"])
        target_user["電話番号"] = request.form.get("phone", target_user["電話番号"])
        target_user["携帯番号"] = request.form.get("mobile", target_user["携帯番号"])
        target_user["紹介者NO"] = request.form.get("ref_no", target_user["紹介者NO"])
        if request.form.get("password"):
            target_user["PASS"] = request.form.get("password")

        with open(USERS_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=target_user.keys())
            writer.writeheader()
            for u in users:
                if u["ID"] == user_id:
                    writer.writerow(target_user)
                else:
                    writer.writerow(u)

        return redirect(url_for("mypage", user_id=user_id))

    return render_template("pages/mypage_edit.html", user=target_user)

# ログアウト
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# -----------------------------
# ナビバー用の追加ルート
# -----------------------------
@app.route("/support")
def support():
    return render_template("pages/support.html")

@app.route("/services")
def services():
    return render_template("pages/suppliers.html")  # サービス一覧 = suppliers.html

@app.route("/news")
def news():
    return render_template("pages/guide.html")  # 仮で guide.html を当てる

@app.route("/settings")
def settings():
    return render_template("pages/setting.html")

# -----------------------------
# ヘルスチェック
# -----------------------------
@app.route("/healthz")
def healthz():
    return "ok", 200

# -----------------------------
# エントリポイント
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
