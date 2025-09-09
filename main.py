from flask import Flask, render_template, Response, session, redirect, url_for, request

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "change-this-secret"  # ← 本番は環境変数で

# 共通: ログイン要求
def require_login():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return None

# Health check（Render）
@app.route("/healthz")
def healthz():
    return Response("OK", status=200, mimetype="text/plain")

# 未ログイン用ホーム（ナビはlayout側で非表示）
@app.route("/")
def index():
    return render_template("pages/home.html")

# ログイン（見た目用の簡易版）
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # 本番はID/PASSチェックを追加
        session["logged_in"] = True
        return redirect(url_for("mypage"))
    return render_template("pages/login.html")

# ログアウト
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# ここから保護ページ（ログイン後のみ）
@app.route("/support")
def support():
    guard = require_login()
    if guard: return guard
    return render_template("pages/support.html")

@app.route("/services")
def services():
    guard = require_login()
    if guard: return guard
    return render_template("pages/services.html")

@app.route("/news")
def news():
    guard = require_login()
    if guard: return guard
    return render_template("pages/news.html")

@app.route("/mypage")
def mypage():
    guard = require_login()
    if guard: return guard
    return render_template("pages/mypage.html")

@app.route("/settings")
def settings():
    guard = require_login()
    if guard: return guard
    return render_template("pages/settings.html")

if __name__ == "__main__":
    app.run(debug=True)
