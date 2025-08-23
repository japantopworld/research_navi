from flask import Flask
from routes.login import login_bp
from routes.register import register_bp
from routes.home import home_bp
# 必要に応じて他のBlueprintも追加

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Blueprint登録
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(home_bp)
# 他にも必要なら順次追加

# Health check route（Render用）
@app.route("/healthz")
def health_check():
    return "OK", 200

if __name__ == "__main__":
    app.run(debug=True)
