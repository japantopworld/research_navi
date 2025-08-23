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

# ヘルスチェック用
@app.route("/healthz")
def healthz():
    return "OK", 200

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
