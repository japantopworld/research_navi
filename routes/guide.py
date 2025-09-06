# routes/guide.py

from flask import Blueprint, render_template
from utils.auth_required import login_required  # ← 認証が必要なら忘れずに

guide_bp = Blueprint('guide_bp', __name__)  # ✅ Blueprint名と一致させる

@guide_bp.route("/guide")
@login_required  # ← 任意：ログイン必須にしたい場合
def guide():
    return render_template("pages/guide.html")
