from flask import Flask, render_template, session, redirect, url_for
from routes.login import login_bp
from routes.register import register_bp
from routes.home import home_bp
from routes.health import health_bp

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Blueprint 登録
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(home_bp)
app.register_blueprint(health_bp)

@app.route("/")
def index():
    return redirect(url_for("home_bp.home"))

if __name__ == "__main__":
    app.run(debug=True)
