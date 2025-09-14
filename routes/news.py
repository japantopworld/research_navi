from flask import Blueprint, render_template

news_bp = Blueprint("news_bp", __name__)

@news_bp.route("/news")
def news():
    return render_template("pages/news.html", unread_count=0)

@news_bp.route("/news/<int:news_id>")
def news_detail(news_id):
    return render_template("pages/news_detail.html", news_id=news_id)
