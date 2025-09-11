# -----------------------------
# ホーム画面
# -----------------------------
@app.route("/home")
def home():
    return render_template("pages/home.html")

# ルートはホームにリダイレクト
@app.route("/")
def index():
    return redirect(url_for("home"))

# ログアウト
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))
