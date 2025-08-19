from flask import Flask
from routes import register, search, ranking  # ← 分割されたルートを読み込む

app = Flask(__name__)

# Blueprint登録
app.register_blueprint(register.bp)
app.register_blueprint(search.bp)
app.register_blueprint(ranking.bp)

@app.route("/")
def home():
    return "🔍 リサーチナビ 起動中"

if __name__ != "__main__":  # Render用に app.run() は不要
    app = app
