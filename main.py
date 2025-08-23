from flask import Flask
from routes.login import login_bp
from routes.register import register_bp
from routes.home import home_bp

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Blueprint 登録
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(home_bp)

# ヘルスチェック用（Render用）
@app.route("/healthz")
def health_check():
    return "OK", 200

# エラーハンドラ：404
@app.errorhandler(404)
def not_found(e):
    return "ページが見つかりませんでした（404）", 404

# エラーハンドラ：500
@app.errorhandler(500)
def server_error(e):
    return "内部サーバーエラー（500）", 500

# アプリ起動
if __name__ == "__main__":
    app.run(debug=True)
