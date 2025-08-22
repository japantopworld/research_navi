import os
import csv
from flask import Flask, render_template, request, redirect, url_for, Blueprint

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

# ルート（ホーム画面）
@app.route("/")
def index():
    return render_template("pages/home.html")

# ヘルスチェック（Render用）
@app.route("/healthz")
def health_check():
    return "ok", 200

# 新規ユーザー登録ページ
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
        file_exists = os.path.isfile(filepath)
        with open(filepath, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=save_data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(save_data)

        return f"✅ 登録完了！割り当てられたIDは {user_id} です"

    return render_template("pages/register_user.html")

# 注意：Renderでは app.run() は不要！
