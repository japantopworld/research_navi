from flask import Blueprint, render_template, request, redirect, url_for, flash
import pandas as pd
import os
from datetime import datetime

accounting_bp = Blueprint('accounting_bp', __name__)
DATA_PATH = "data/transactions.csv"

@accounting_bp.route("/accounting", methods=["GET", "POST"])
def accounting():
    if request.method == "POST":
        date = request.form["date"]
        item = request.form["item"]
        category = request.form["category"]
        platform = request.form["platform"]
        revenue = float(request.form["revenue"] or 0)
        cost = float(request.form["cost"] or 0)
        fee = float(request.form["fee"] or 0)
        shipping = float(request.form["shipping"] or 0)
        expense = float(request.form["expense"] or 0)
        tags = request.form["tags"]

        profit = revenue - cost - fee - shipping - expense
        roi = (profit / cost) * 100 if cost > 0 else 0

        df = pd.DataFrame([{
            "date": date,
            "item": item,
            "category": category,
            "platform": platform,
            "revenue": revenue,
            "cost": cost,
            "fee": fee,
            "shipping": shipping,
            "expense": expense,
            "profit": profit,
            "roi": roi,
            "tags": tags
        }])

        if not os.path.exists(DATA_PATH):
            df.to_csv(DATA_PATH, index=False)
        else:
            df.to_csv(DATA_PATH, mode="a", header=False, index=False)

        flash("保存しました ✅")
        return redirect(url_for("accounting_bp.accounting"))

    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.to_period("M")
        summary = df.groupby("month")[["revenue", "cost", "fee", "shipping", "expense", "profit"]].sum().reset_index()
        top_roi = df.sort_values(by="roi", ascending=False).head(10)
    else:
        df = pd.DataFrame()
        summary = pd.DataFrame()
        top_roi = pd.DataFrame()

    return render_template("pages/accounting.html", data=df, summary=summary, top_roi=top_roi)
