from flask import Blueprint, render_template
import csv

history_bp = Blueprint('history_bp', __name__, url_prefix='/buyer/history')

@history_bp.route('/', methods=['GET'])
def history_page():
    records = []
    try:
        with open('data/search_history.csv', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            records = list(reader)
    except FileNotFoundError:
        pass
    return render_template('pages/buyer/history.html', records=records)