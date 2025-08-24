from flask import Flask
from routes.login import login_bp
from routes.register import register_bp
from routes.home import home_bp

app = Flask(__name__)
app.secret_key = "your_secret_key"  # セッション用の秘密鍵（適宜変更）

# Blueprint 登録
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(home_bp)

# Health check（Render でのタイムアウト対策用）
@app.route("/healthz")
def healthz():
    return "ok", 200

# アプリ起動
if __name__ == "__main__":
    app.run(debug=True)
