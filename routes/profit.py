from flask import Blueprint, render_template, request

profit_bp = Blueprint('profit_bp', __name__, url_prefix='/profit')

@profit_bp.route('/', methods=['GET'])
def profit_page():
    keyword = request.args.get('keyword', '')
    return render_template('pages/buyer/profit.html', keyword=keyword)