from flask import Flask, render_template, Response, session, redirect, url_for, request

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "change-this-secret"  # 本番は環境変数で設定してください

# -------- Health check (Render 用) --------
@app.route("/healthz")
def healthz():
    return Response("OK", status=200, mimetype="text/plain")

# -------- ホーム --------
@app.route("/")
def index():
    return render_template("pages/home.html")

# -------- ログイン（見た目用の最小実装）--------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # TODO: 本番実装ではID/パスワードの検証を行う
        session["logged_in"] = True
        return redirect(url_for("index"))
    return render_template("auth/login.html")

# -------- 新規登録（見た目用。auth/register.html を使用）--------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # TODO: 本番実装ではユーザー作成処理を行い、成功時にログイン or ログインページへ
        return redirect(url_for("login"))
    return render_template("auth/register.html")

# -------- ログアウト --------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    # Render では Proc/起動コマンドで waitress を使う想定
    app.run(debug=True)
