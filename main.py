import os, csv, re
from datetime import datetime
from flask import request, render_template, redirect, url_for

DATA_DIR = os.path.join("research_navi", "data")
USERS_CSV = os.path.join(DATA_DIR, "users.csv")

def ensure_users_csv():
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
    """
    入力: KA / Kb1 / B1 / a / A など
    出力: 先頭K/kは除去 → 先頭英字(A〜E) + 任意の数字1桁(あれば)
          例 KA -> A, KB1 -> B1, b1 -> B1, Kc -> C
    不正は空文字を返す
    """
    if not raw:
        return ""
    s = raw.strip().upper()
    if s.startswith("K"):
        s = s[1:]
    # A〜E + (数字1桁任意)
    m = re.fullmatch(r"([A-E])([0-9])?", s)
    if not m:
        return ""
    alpha, digit = m.group(1), (m.group(2) or "")
    return f"{alpha}{digit}"

@app.route("/register", methods=["GET", "POST"])
def register():
    ensure_users_csv()

    if request.method == "POST":
        name = request.form.get("name","").strip()
        kana = request.form.get("kana","").strip()
        birth = request.form.get("birth","").strip()        # YYYY-MM-DD
        branch = request.form.get("branch","A").strip()     # A〜E
        phone = request.form.get("phone","").strip()
        mobile = request.form.get("mobile","").strip()
        email = request.form.get("email","").strip()
        dept = request.form.get("dept","").strip()

        # ここがポイント：紹介者NOは自由入力（KA/KB1）→ 正規化
        ref_raw = request.form.get("ref_raw","").strip()
        ref_norm = normalize_ref(ref_raw)                   # A / B1 など

        password = request.form.get("password","")
        password2 = request.form.get("password2","")

        mmdd = mmdd_from_birth(birth)
        # 新仕様：ユーザーID = 紹介者NO(正規化後) + MMDD + 枝
        user_id = f"{ref_norm}{mmdd}{branch}" if ref_norm and mmdd and branch else ""

        errors = []
        if not name: errors.append("氏名は必須です。")
        if not kana: errors.append("ふりがなは必須です。")
        if not birth: errors.append("生年月日は必須です。")
        if not mmdd: errors.append("生年月日からMMDDが生成できません。形式を確認してください。")
        if branch not in list("ABCDE"): errors.append("枝は A〜E を選択してください。")

        # 紹介者NO（正規化）
        if not ref_norm:
            errors.append("紹介者NOの形式が不正です。例：KA / KB1（保存時は K 除去で A / B1 になります）")

        # ユーザーID
        if not user_id: errors.append("ユーザーIDの生成に失敗しました。")
        if user_id and id_exists(user_id): errors.append("このユーザーIDはすでに登録されています。")

        # パスワード
        if not password or len(password) < 6:
            errors.append("パスワードは6文字以上で入力してください。")
        if password != password2:
            errors.append("確認用パスワードが一致しません。")

        if errors:
            form = dict(request.form)
            form["ref_no"] = ref_norm           # 表示用：正規化後
            form["user_id"] = user_id
            return render_template("auth/register.html", errors=errors, form=form)

        age = calc_age(birth)
        with open(USERS_CSV, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                name, kana, birth, age, phone, mobile,
                email, dept, ref_norm, user_id, password
            ])

        return redirect(url_for("login"))

    return render_template("auth/register.html")
