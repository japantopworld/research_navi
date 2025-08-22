from flask import Blueprint

health_bp = Blueprint("health_bp", __name__)

@health_bp.route("/healthz")
def healthz():
    return "OK", 200
