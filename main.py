from flask import Flask, render_template
from routes.static_pages import static_pages_bp
from routes.register import register_bp
from routes.search import search_bp
from routes.ranking import ranking_bp

app = Flask(__name__)

# Blueprint登録
app.register_blueprint(static_pages_bp)
app.register_blueprint(register_bp)
app.register_blueprint(search_bp)
app.register_blueprint(ranking_bp)

# ホーム（トップページ）
@app.route("/")
def home():
    return render_template("pages/dashboard.html")

# ✅ Renderのヘルスチェック用ルート
@app.route("/healthz")
def healthz():
    return "OK", 200

# 開発ローカル用（Renderでは使用されません）
if __name__ == "__main__":
    app.run(debug=True)
