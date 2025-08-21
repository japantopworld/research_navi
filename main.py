from flask import Flask
from routes.search import search_bp
from routes.ranking import ranking_bp
from routes.register import register_bp
from routes.login import login_bp  # ← ログインルート

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Blueprint 登録（1回だけ、追記禁止）
app.register_blueprint(search_bp)
app.register_blueprint(ranking_bp)
app.register_blueprint(register_bp)
app.register_blueprint(login_bp)

# ホームルート
@app.route('/')
def home():
    return "✅ ホーム画面またはログイン画面にリダイレクト予定"

# Render 用
if __name__ == "__main__":
    app.run(debug=True)
