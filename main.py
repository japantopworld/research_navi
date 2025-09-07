from flask import Flask, redirect, url_for, session

app = Flask(__name__, template_folder='templates')
app.secret_key = 'your_secret_key'

@app.route('/register', methods=['GET', 'POST'])
def direct_register():
    return "<h1>Register route direct from main.py</h1>"

@app.route('/login')
def login():
    return "<h1>ログインページ（仮）</h1>"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/healthz')
def healthz():
    return "OK"

@app.route('/test-register')
def test_register():
    return "Register route is working"

@app.route('/routes')
def show_routes():
    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = f"{rule.endpoint:30s} {methods:20s} {rule.rule}"
        output.append(line)
    return "<pre>" + "\n".join(output) + "</pre>"
