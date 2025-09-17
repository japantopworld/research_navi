from flask import Blueprint, render_template

logistics_bp = Blueprint("logistics_bp", __name__)

@logistics_bp.route("/logistics")
def logistics_home():
    return render_template("pages/logistics/index.html")

@logistics_bp.route("/logistics/inventory")
def inventory():
    return render_template("pages/logistics/inventory.html")

@logistics_bp.route("/logistics/shipping")
def shipping():
    return render_template("pages/logistics/shipping.html")

@logistics_bp.route("/logistics/layout")
def layout():
    return render_template("pages/logistics/layout.html")
