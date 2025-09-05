# routes/health_check.py

from flask import Blueprint

health_check_bp = Blueprint("health_check_bp", __name__)

@health_check_bp.route("/healthz")
def healthz():
    return "OK", 200
