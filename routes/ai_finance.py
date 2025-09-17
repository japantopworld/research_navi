# research_navi/routes/ai_finance.py
from flask import Blueprint, render_template

ai_finance_bp = Blueprint("ai_finance_bp", __name__, url_prefix="/ai_finance")

@ai_finance_bp.route("/")
def ai_finance_home():
    return render_template("pages/ai_finance/home.html")
