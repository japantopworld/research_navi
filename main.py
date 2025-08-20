# main.py
from flask import Flask, render_template
from routes import register

app = Flask(__name__)

# Blueprint登録
app.register_blueprint(register.register_bp)

@app.route("/")
def home():
    return render_template("pages/home.html")

# 他のBlueprintもあれば同様に登録（例）
# from routes import search
# app.register_blueprint(search.search_bp)

if __name__ == "__main__":
    app.run(debug=True)
