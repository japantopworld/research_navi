from flask import Flask, redirect, url_for, session

app = Flask(__name__, template_folder='templates')
app.secret_key = 'your_secret_key'

# ✅ /register を直接定義（Blueprintなし）
@app.route('/register', methods=['GET', 'POST'])
def direct_register():
    return "<h1>Register route direct from main.py</h1>"

# ✅ /login（仮のログインページ）
@app.route('/login')
def login():
    return "<h1>ログインページ（仮）</h1>"

# ✅ /logout（セッション削除）
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ✅ Render 用ヘルスチェック
@app.route('/healthz')
def healthz():
    return "OK"

# ✅ テストルート（Flaskが動いているか確認）
@app.route('/test-register')
def test_register():
    return "Register route is working"

# ✅ ルート一覧表示（Flaskが認識しているURLを確認）
@app.route('/routes')
def show_routes():
    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = f"{rule.endpoint:30s} {methods:20s} {rule.rule}"
        output.append(line)
    return "<pre>" + "\n".join(output) + "</pre>"
if __name__ == "__main__":
    app.run()
