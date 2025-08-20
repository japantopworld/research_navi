from flask import Blueprint, render_template

guide_bp = Blueprint('guide', __name__)

@guide_bp.route("/guide")
def guide():
    return render_template("pages/guide.html")
