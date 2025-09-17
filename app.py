# -*- coding: utf-8 -*-
import os
from flask import Flask
from .routes.buyer import buyer_bp

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "devkey")
    app.register_blueprint(buyer_bp, url_prefix="/buyer")

    @app.route("/")
    def index():
        from flask import render_template
        return render_template("pages/buyer/home.html")

    @app.route("/healthz")
    def healthz():
        return "ok", 200

    return app

app = create_app()
