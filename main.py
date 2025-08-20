from flask import Flask, render_template
from routes import dashboard, search, ranking, register, guide  # 必要なBlueprintをすべてインポート

app = Flask(__name__)

# Blueprint登録
app.register_blueprint(dashboard.dashboard_bp)
app.register_blueprint(search.search_bp)
app.register_blueprint(ranking.ranking_bp)
app.register_blueprint(register.register_bp)
app.register_blueprint(guide.guide_bp)  # 使い方ページ

# ホームページ
@app.route("/")
def home():
    return render_template("pages/home.html")

# エラーページ
@app.errorhandler(404)
def page_not_found(e):
    return render_template("pages/404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)
