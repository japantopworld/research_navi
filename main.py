from flask import Flask, render_template, Response, session, redirect, url_for, request

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "change-this-secret"  # 本番は環境変数にすることを推奨

# Render用ヘルスチェック
@app.route("/healthz")
def healthz():
    return Response("OK", status=200, mimetype="text/plain")

# ホーム
@app.route("/")
def index():
    return render_template("pages/home.html")

# ログイン（プレースホルダー）
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["logged_in"] = True
        return redirect(url_for("index"))
    return render_template("auth/login.html")  # ← auth フォルダに login.html がある前提

# 新規登録（auth/register.html を利用）
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # TODO: ユーザー登録処理を追加予定
        return redirect(url_for("login"))
    return render_template("auth/register.html")

# ログアウト
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
