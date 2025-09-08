# main.py
import os
from flask import Flask, render_template, Response

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
app.config["TEMPLATES_AUTO_RELOAD"] = True

# 1) Health check（Render用）
@app.route("/healthz")
def healthz():
    return Response("ok", status=200, mimetype="text/plain")

# 2) auth_bp（/login, /logout, /register）
try:
    from routes.auth import auth_bp   # ← あなたが貼ってくれた auth_bp のファイル
    app.register_blueprint(auth_bp)   # ← url_prefix は付けない
except Exception as e:
    print(f"[WARN] auth_bp register failed: {e}")

# 3) トップページ（templates/pages/home.html を表示）
@app.route("/")
def index():
    return render_template("pages/home.html")

# 4) 404/500（テンプレ無い時も落ちない）
@app.errorhandler(404)
def not_found(e):
    return Response("404 Not Found", status=404)

@app.errorhandler(500)
def server_error(e):
    return Response("500 Internal Server Error", status=500)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
