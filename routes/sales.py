
from flask import Blueprint, render_template
sales_bp = Blueprint('sales_bp', __name__)

@sales_bp.route('/sales/history')
def sales_history():
    return render_template('pages/sales/sales_history.html')

@sales_bp.route('/sales/graph')
def sales_graph():
    return render_template('pages/sales/sales_graph.html')
