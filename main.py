from flask import Flask, render_template
from routes.login import login_bp
from routes.register import register_bp
from routes.mypage import mypage_bp
from routes.pages import pages_bp

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Blueprint 登録
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(mypage_bp)
app.register_blueprint(pages_bp)

# ✅ 最初のホーム画面表示（ログインではなく home.html）
@app.route("/")
def index():
    return render_template("pages/home.html")

# ✅ Render 用のヘルスチェック（タイムアウト対策）
@app.route("/healthz")
def health_check():
    return "ok", 200

# 🔸 ローカル実行用（Renderでは使われないが残してOK）
if __name__ == "__main__":
    app.run(debug=True)
