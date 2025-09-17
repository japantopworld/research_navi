
from flask import Blueprint, render_template, request, redirect, url_for, flash
listing_bp = Blueprint('listing_bp', __name__)

@listing_bp.route('/listing/ai', methods=['GET', 'POST'])
def ai_listing():
    if request.method == 'POST':
        title = request.form.get('title')
        desc = "これはAIが生成した説明文です：" + title
        return render_template('pages/sales/ai_listing.html', result=desc)
    return render_template('pages/sales/ai_listing.html')

@listing_bp.route('/listing/review')
def listing_review():
    return render_template('pages/sales/listing_review.html')
