from flask import Flask, render_template, session, redirect, url_for
from login import login_bp
from register import register_bp

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Blueprint 登録
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)

@app.route("/")
def home():
    return render_template("pages/home.html")

@app.route("/healthz")
def healthz():
    return "OK", 200

if __name__ == "__main__":
    app.run(debug=True)
