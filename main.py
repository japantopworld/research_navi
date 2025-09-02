from flask import Flask, render_template
from routes.login import login_bp
from routes.register import register_bp
from routes.pages import pages_bp
from routes.mypage import mypage_bp

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Blueprint登録
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(pages_bp)
app.register_blueprint(mypage_bp)

# ✅ 最初の画面をホーム画面に変更
@app.route("/")
def home():
    return render_template("pages/home.html")

# ✅ Renderのヘルスチェック用
@app.route("/healthz")
def health_check():
    return "ok"

if __name__ == "__main__":
    app.run(debug=True)
