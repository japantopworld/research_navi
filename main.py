from flask import Flask
from routes import login, register, mypage, mypage_edit  # 各Blueprintの読み込み

app = Flask(__name__)
app.secret_key = "your_secret_key"  # セッション用の秘密鍵（適宜変更）

# Blueprint登録
app.register_blueprint(login.login_bp)
app.register_blueprint(register.register_bp)
app.register_blueprint(mypage.mypage_bp)
app.register_blueprint(mypage_edit.mypage_edit_bp)

# ヘルスチェック用（Renderのタイムアウト防止用）
@app.route("/healthz")
def health_check():
    return "OK", 200

# ホーム（未ログイン時はリダイレクトさせてもOK）
@app.route("/")
def index():
    return "Welcome to Research Navi App"

if __name__ == "__main__":
    app.run(debug=True)
