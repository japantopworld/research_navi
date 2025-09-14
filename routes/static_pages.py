from flask import Blueprint, render_template

# Blueprint 定義
static_pages_bp = Blueprint("static_pages", __name__)

# 使い方ガイド
@static_pages_bp.route("/guide")
def guide():
    return render_template("pages/guide.html")

# 利用規約
@static_pages_bp.route("/terms")
def terms():
    return render_template("pages/terms.html")

# プライバシーポリシー
@static_pages_bp.route("/privacy")
def privacy():
    return render_template("pages/privacy.html")

# よくある質問（FAQ）
@static_pages_bp.route("/faq")
def faq():
    return render_template("pages/faq.html")

# お問い合わせフォーム
@static_pages_bp.route("/contact")
def contact():
    return render_template("pages/contact.html")

# サポート（まとめページ）
@static_pages_bp.route("/support")
def support():
    return render_template("pages/support.html")
