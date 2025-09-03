from flask import Flask
from routes.login import login_bp
from routes.register import register_bp
from routes.home import home_bp
from routes.mypage import mypage_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Blueprint登録
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(home_bp)
app.register_blueprint(mypage_bp)

# ホームルート
@app.route('/')
def index():
    return """
    <h1>🏠 ホーム画面</h1>
    <ul>
      <li><a href="/login">ログイン</a></li>
      <li><a href="/register">新規登録</a></li>
      <li><a href="/mypage">マイページ</a></li>
    </ul>
    <p>制作者：鳳陽合同会社　小島崇彦</p>
    <img src="/static/img/mascot.png" width="200">
    """

if __name__ == '__main__':
    app.run(debug=True)
