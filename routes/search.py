# routes/search.py

from flask import Blueprint, render_template

search_bp = Blueprint('search_bp', __name__)

@search_bp.route("/search")
def search():
    return render_template("pages/search.html")
