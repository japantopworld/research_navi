from flask import Flask, render_template, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route("/")
def home():
    return "✅ リサーチナビは起動しています！"

@app.route("/mypage")
def mypage():
    # 未ログイン時はログインページへ
    if not session.get("user_id"):
        return redirect(url_for("login"))

    # 親ユーザーだけアクセス許可
    if session.get("role") == "parent":
        return render_template("pages/mypage_parent.html")
    else:
        return "アクセス権がありません", 403
