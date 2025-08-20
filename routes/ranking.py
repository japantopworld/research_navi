from flask import Blueprint, render_template

ranking_bp = Blueprint('ranking', __name__)

@ranking_bp.route("/ranking")
def ranking():
    return render_template("pages/ranking.html")

