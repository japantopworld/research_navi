from flask import Blueprint, render_template

policy_bp = Blueprint("policy_bp", __name__)

@policy_bp.route("/terms")
def terms():
    return render_template("policy/terms.html")
