# routes/guide.py

from flask import Blueprint, render_template

guide_bp = Blueprint('guide_bp', __name__)  # Blueprint名を明示

@guide_bp.route("/guide", endpoint="guide_page")  # ✅ エンドポイント名を guide_page に統一
def guide_page():
    return render_template("pages/guide.html")
