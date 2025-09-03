from flask import Flask
from routes.mypage import mypage_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Blueprint登録
app.register_blueprint(mypage_bp)

@app.route('/')
def index():
    return '<h1>ホーム画面（後で整備）</h1><a href="/mypage">マイページへ</a>'

if __name__ == '__main__':
    app.run(debug=True)
