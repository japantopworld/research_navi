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
    return render_template("auth/login.html")  # ← ない場合はプレースホルダを作成してください

# -------- 新規登録（見た目用。auth/register.html を使用）--------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # TODO: 本番実装ではユーザー作成処理を行い、成功時にログイン or ログインページへ
        return redirect(url_for("login"))
    return render_template("auth/register.html")  # ← ない場合はプレースホルダを作成してください

# -------- ログアウト --------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# --------- ここからはナビ用（存在しないと url_for で 500 になるためプレースホルダー） ---------
@app.route("/support")
def support():
    # 後でテンプレに差し替えOK（まず 200 を返す）
    return Response("サポート（プレースホルダー）", status=200, mimetype="text/plain")

@app.route("/services")
def services():
    return Response("サービス一覧（プレースホルダー）", status=200, mimetype="text/plain")

@app.route("/news")
def news():
    return Response("お知らせ一覧（プレースホルダー）", status=200, mimetype="text/plain")

@app.route("/mypage")
def mypage():
    return Response("マイページ（プレースホルダー）", status=200, mimetype="text/plain")

@app.route("/settings")
def settings():
    return Response("各種設定（プレースホルダー）", status=200, mimetype="text/plain")
# --------- プレースホルダーここまで ---------

# （任意）デバッグ用：現在のルートを確認したい場合のみ有効化
# @app.route("/__routes")
# def __routes():
#     lines = [f"{r.endpoint} -> {r}" for r in app.url_map.iter_rules()]
#     return Response("\n".join(lines), mimetype="text/plain")

if __name__ == "__main__":
    # Render では Proc/起動コマンドで waitress を使う想定
    app.run(debug=True)
