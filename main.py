import os
import csv
from flask import Flask, render_template, request

app = Flask(__name__)

# 職種コードマッピング
position_map = {
    "経理": "ACC",
    "バイヤー": "BUY",
    "販売": "SAL",
    "物流": "LOG",
    "統括": "SUP",
    "総合": "GEN"
}

@app.route("/users/register", methods=["GET", "POST"])
def register_user():
    if request.method == "POST":
        # フォームデータ取得
        username = request.form["username"]
        furigana = request.form["furigana"]
        birthdate = request.form["birthdate"]  # YYYY-MM-DD
        age = request.form["age"]
        tel = request.form["tel"]
        mobile = request.form["mobile"]
        email = request.form["email"]
        department = request.form["department"]
        position_jp = request.form["position"]
        ref_code_full = request.form["ref_code"].upper()  # 例：KA、KB、KC
        password = request.form["password"]

        # 【1】紹介者コード（例：KA → A）
        ref_letter = ref_code_full[-1]

        # 【2】誕生日 → MMDD（西暦は使わない）
        birth_mmdd = birthdate[5:7] + birthdate[8:10]

        # 【3】枝番号カウント（紹介者ごとに通し番号）
        filepath = os.path.join("data", "users.csv")
        branch_no = 1
        existing_rows = []

        if os.path.exists(filepath):
            with open(filepath, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing_rows.append(row)
                    if row["紹介者NO"] == ref_letter and row["枝番号"].startswith(ref_letter):
                        branch_no += 1

        branch_code = f"{ref_letter}{branch_no}"  # 例：A1, B3

        # 【4】職種コード
        position_code = position_map.get(position_jp)
        if not position_code:
            return "❌ 無効な職種です"

        # 【5】ID生成：職種コード + 紹介者 + MMDD + 枝番号
        user_id = f"{position_code}{ref_letter}{birth_mmdd}{branch_code}"

        # 【6】保存データ
        save_data = {
            "ユーザー名": username,
            "ユーザー名ふり仮名": furigana,
            "生年月日": birthdate,
            "年齢": age,
            "電話番号": tel,
            "携帯番号": mobile,
            "メールアドレス": email,
            "部署": department,
            "紹介者NO": ref_letter,
            "ID": user_id,
            "PASS": password,
            "枝番号": branch_code
        }

        # 【7】CSV保存
        os.makedirs("data", exist_ok=True)
        file_exists = os.path.isfile(filepath)
        with open(filepath, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=save_data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(save_data)

        return f"✅ 登録完了！割り当てられたIDは {user_id} です"

    return render_template("register_user.html")


# ✅ / ルート：Renderの起動確認に使われる
@app.route("/")
def index():
    return "✅ アプリは正常に起動しています！（/）"

# ✅ /healthz：RenderのHealth Check用
@app.route("/healthz")
def healthz():
    return "ok", 200
