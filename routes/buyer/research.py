from flask import Blueprint, render_template, request
from utils.search_utils import generate_search_links, ai_predict_product_name, save_search_history
import os
from werkzeug.utils import secure_filename

research_bp = Blueprint('research_bp', __name__, url_prefix='/buyer/research')

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@research_bp.route('/', methods=['GET'])
def research_page():
    return render_template('pages/buyer/research.html')

@research_bp.route('/search', methods=['GET'])
def search_by_keyword():
    keyword = request.args.get('keyword')
    results = generate_search_links(keyword)
    save_search_history(keyword, "キーワード検索")
    return render_template('pages/buyer/research.html', results=results, keyword=keyword)

@research_bp.route('/image_search', methods=['POST'])
def search_by_image():
    file = request.files.get('image')
    if not file:
        return render_template('pages/buyer/research.html', error='ファイルが選択されていません')

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    suggested_name = ai_predict_product_name(filepath)
    results = generate_search_links(suggested_name)
    save_search_history(suggested_name, "画像検索")

    return render_template('pages/buyer/research.html', results=results, suggested_name=suggested_name)
