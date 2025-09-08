from flask import Flask
from routes.home import home_bp
from routes.search import search_bp
from routes.ranking import ranking_bp
from routes.guide import guide_bp
from routes.auth import auth_bp
from routes.health_check import health_check_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッション管理のために必須

# Blueprint 登録
app.register_blueprint(home_bp)
app.register_blueprint(search_bp)
app.register_blueprint(ranking_bp)
app.register_blueprint(guide_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(health_check_bp)

# Health check endpoint for Render
@app.route('/healthz')
def healthz():
    return "OK"
from flask import Flask
from routes.home import home_bp
from routes.search import search_bp
from routes.ranking import ranking_bp
from routes.guide import guide_bp
from routes.auth import auth_bp
from routes.health_check import health_check_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッション管理のために必須

# Blueprint 登録
app.register_blueprint(home_bp)
app.register_blueprint(search_bp)
app.register_blueprint(ranking_bp)
app.register_blueprint(guide_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(health_check_bp)

# Health check endpoint for Render
@app.route('/healthz')
def healthz():
    return "OK"
from flask import Flask
from routes.home import home_bp
from routes.search import search_bp
from routes.ranking import ranking_bp
from routes.guide import guide_bp
from routes.auth import auth_bp
from routes.health_check import health_check_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッション管理のために必須

# Blueprint 登録
app.register_blueprint(home_bp)
app.register_blueprint(search_bp)
app.register_blueprint(ranking_bp)
app.register_blueprint(guide_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(health_check_bp)

# Health check endpoint for Render
@app.route('/healthz')
def healthz():
    return "OK"
