# -*- coding: utf-8 -*-
import os
import pandas as pd
from datetime import datetime, timezone, timedelta
from flask import Flask, render_template

app = Flask(__name__, template_folder="templates", static_folder="static")

# CSVパス
DATA_PATH = os.path.join("data", "transactions.csv")
STOCK_PATH = os.path.join("data", "stock.csv")
ALERT_PATH = os.path.join("data", "alerts.csv")
JST = timezone(timedelta(hours=9))

# CSV読み込み（安全版）
def safe_read_csv(path, columns):
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            for c in columns:
                if c not in df.columns:
                    df[c] = None
            return df[columns]
        except Exception:
            return pd.DataFrame(columns=columns)
    else:
        return pd.DataFrame(columns=columns)

# ヘルスチェック
@app.route("/healthz")
def healthz():
    return "ok", 200

# ホーム
@app.route("/")
def home():
    return render_template("pages/dashboard/home.html")

# ダッシュボード
@app.route("/dashboard")
def dashboard():
    tx_cols = ["date", "platform", "revenue", "cost", "profit"]
    df = safe_read_csv(DATA_PATH, tx_cols)
    stock_df = safe_read_csv(STOCK_PATH, ["item", "stock", "category", "updated_at"])
    alert_df = safe_read_csv(ALERT_PATH, ["date", "message", "level"])

    today = datetime.now(JST).date()
    today_str = today.strftime("%Y-%m-%d")
    year_month = today.strftime("%Y-%m")

    for col in ["revenue", "cost", "profit"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    today_sales = df.loc[df["date"] == today_str, "revenue"].sum()
    today_profit = df.loc[df["date"] == today_str, "profit"].sum()
    monthly_sales = df.loc[df["date"].str.startswith(year_month, na=False), "revenue"].sum()
    monthly_profit = df.loc[df["date"].str.startswith(year_month, na=False), "profit"].sum()

    df_dates = df.copy()
    if not df_dates.empty:
        df_dates["date"] = pd.to_datetime(df_dates["date"], errors="coerce").dt.date
    else:
        df_dates["date"] = pd.to_datetime(pd.Series([], dtype="datetime64[ns]"))

    last7 = [today - timedelta(days=i) for i in range(6, -1, -1)]
    chart_df = pd.DataFrame({"date": last7})
    chart_df["revenue"] = chart_df["date"].apply(
        lambda d: df_dates.loc[df_dates["date"] == d, "revenue"].sum() if "revenue" in df_dates else 0
    )
    chart_labels = [d.strftime("%m/%d") for d in chart_df["date"]]
    chart_values = chart_df["revenue"].tolist()

    try:
        stock_df["stock"] = pd.to_numeric(stock_df["stock"], errors="coerce").fillna(0).astype(int)
        stock_top5 = stock_df.sort_values("stock", ascending=False).head(5)
    except Exception:
        stock_top5 = stock_df.head(5)

    if not alert_df.empty:
        try:
            alert_df["date_dt"] = pd.to_datetime(alert_df["date"], errors="coerce")
            alert_df = alert_df.sort_values("date_dt", ascending=False)
        except Exception:
            pass
    alert_top5 = alert_df.head(5)

    return render_template(
        "pages/dashboard/dashboard.html",
        today_sales=round(float(today_sales), 0),
        today_profit=round(float(today_profit), 0),
        monthly_sales=round(float(monthly_sales), 0),
        monthly_profit=round(float(monthly_profit), 0),
        stock_df=stock_top5,
        alert_df=alert_top5,
        chart_labels=chart_labels,
        chart_values=chart_values
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
