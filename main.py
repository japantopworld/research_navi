from flask import Flask
from routes.home import home_bp
from routes.login import login_bp
from routes.register import register_bp

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Blueprint登録
app.register_blueprint(home_bp)
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)

@app.route("/")
def index():
    return "<h1>トップページ（仮）</h1><a href='/login'>ログインへ</a>"

# Renderデプロイ用
@app.route("/healthz")
def health_check():
    return "ok"

if __name__ == "__main__":
    app.run(debug=True)
