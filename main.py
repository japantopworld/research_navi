from flask import Flask, render_template
from routes.login import login_bp
from routes.dashboard import dashboard_bp
from routes.ranking import ranking_bp
from routes.search import search_bp

app = Flask(__name__)

# Blueprint登録（順番は自由）
app.register_blueprint(login_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(ranking_bp)
app.register_blueprint(search_bp)

# ホーム画面
@app.route('/')
def home():
    return render_template("pages/home.html")

# ヘルスチェック
@app.route('/healthz')
def healthz():
    return 'OK'

# 404エラーページ
@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404

# 500エラーページ
@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
