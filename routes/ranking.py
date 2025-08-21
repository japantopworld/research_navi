# routes/ranking.py
from flask import Blueprint, render_template
from utils.auth_required import login_required

ranking_bp = Blueprint('ranking_bp', __name__)

@ranking_bp.route("/ranking")
@login_required
def ranking():
    return render_template("pages/ranking.html")
