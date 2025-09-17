# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..services.price_math import calc_profit
from ..services.data_io import read_csv, write_csv, append_order, set_order_status, seed_if_empty
import random, datetime as dt

buyer_bp = Blueprint("buyer_bp", __name__, template_folder="../templates", static_folder="../static")

@buyer_bp.before_app_request
def ensure_seed():
    seed_if_empty()

@buyer_bp.route("/")
def buyer_home():
    kpis = {"scans_today": random.randint(5,20)}
    return render_template("pages/buyer/home.html", kpis=kpis, alerts=read_csv("alerts.csv"), chart_data={})

@buyer_bp.route("/research")
def buyer_research():
    q = request.args.get("q")
    results = []
    if q:
        for i in range(3):
            cost = random.randint(1000,3000)
            price = cost + random.randint(200,1000)
            results.append({"name":f"{q}サンプル{i+1}","vendor":"Amazon","market":"メルカリ","cost":cost,"price":price,"profit":price-cost})
    return render_template("pages/buyer/research.html", q=q, results=results, history={})

@buyer_bp.route("/profit", methods=["GET","POST"])
def buyer_profit():
    form = {"cost":0,"price":0,"shipping":0,"fee_pct":10.0,"rebate_pct":0.0,"coupon":0.0}
    result=None
    if request.method=="POST":
        for k in form: form[k]=float(request.form.get(k,0))
        result=calc_profit(**form)
    return render_template("pages/buyer/profit.html", form=form, result=result)

@buyer_bp.route("/orders", methods=["GET","POST"])
def buyer_orders():
    if request.method=="POST":
        append_order(request.form.get("name"),request.form.get("qty","1"),request.form.get("vendor"),request.form.get("owner"))
        flash("追加しました")
        return redirect(url_for("buyer_bp.buyer_orders"))
    return render_template("pages/buyer/orders.html", orders=read_csv("orders.csv"))

@buyer_bp.route("/orders/<oid>/status/<to>")
def buyer_order_status(oid,to):
    set_order_status(oid,to)
    return redirect(url_for("buyer_bp.buyer_orders"))
