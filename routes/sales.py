# routes/sales.py
# -*- coding: utf-8 -*-
from flask import Blueprint, render_template

sales_bp = Blueprint(
    "sales_bp",
    __name__,
    url_prefix="/sales",   # 部署ごとにプレフィックスを付与
    template_folder="../templates",
    static_folder="../static"
)

@sales_bp.route("/")
def sales_home():
    """販売部のホーム画面"""
    return render_template("pages/sales/home.html")
