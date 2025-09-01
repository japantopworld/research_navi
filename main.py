from flask import Flask, redirect, url_for, session
from routes.login import login_bp
from routes.register import register_bp
from routes.logout import logout_bp
from routes.mypage import mypage_bp

app = Flask(__name__)
app.secret_key = "your_secret_key"  # セッション用

# Blueprint 登録
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(logout_bp)
app.register_blueprint(mypage_bp)

# ルート：ログイン済みならマイページへ、未ログインならログインへ
@app.route("/")
def index():
    if "user_info" in session:
        return redirect(url_for("mypage_bp.mypage"))
    else:
        return redirect(url_for("login_bp.login"))

# Health check (Render用)
@app.route("/healthz")
def health_check():
    return "OK", 200

if __name__ == "__main__":
    app.run(debug=True)
