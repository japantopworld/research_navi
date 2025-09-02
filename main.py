from flask import Flask
from routes.login import login_bp
from routes.register import register_bp
from routes.pages import pages_bp

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Blueprint登録
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(pages_bp)

# 初期ルート（ログインページへ）
@app.route("/")
def index():
    return "<a href='/login'>ログインはこちら</a>"

# Renderでヘルスチェック用
@app.route("/healthz")
def health_check():
    return "ok"

if __name__ == "__main__":
    app.run(debug=True)
