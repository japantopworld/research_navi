from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '<h1>Hello Flask!</h1>'
@app.route('/register', methods=['GET', 'POST'])
def register():
    return "<h1>Register route direct from main.py</h1>"
