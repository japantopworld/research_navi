@app.route("/login", methods=["GET", "POST"])
@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        input_id = request.form.get("username","").strip()
        input_pass = request.form.get("password","").strip()

        # users.csv 認証チェック
        ensure_users_csv()
        with open(USERS_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            user = next((row for row in reader if row["ID"] == input_id and row["PASS"] == input_pass), None)

        if user:
            # 認証成功 → セッション保存 & マイページへ
            session["logged_in"] = True
            session["user_id"] = user["ID"]
            return redirect(url_for("mypage", user_id=user["ID"]))
        else:
            # 認証失敗 → 再表示
            return render_template("auth/login.html", error="ユーザーIDまたはパスワードが違います")

    return render_template("auth/login.html")
