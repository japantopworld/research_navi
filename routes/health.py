# routes/health.py
from flask import Blueprint

health_bp = Blueprint("health", __name__)

@health_bp.route("/healthz")
def health_check():
    return "OK", 200
