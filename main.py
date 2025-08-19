import os, csv, json, ssl, smtplib, traceback
from io import StringIO, BytesIO
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, send_file, jsonify
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, func
from werkzeug.utils import secure_filename

# =============================================================================
# Flask / DB
# =============================================================================
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "research-navi-dev")

# Render/Postgres 対応（postgresql:// → postgresql+psycopg://）
raw_db_url = os.getenv("DATABASE_URL", "sqlite:///data/app.db")
if raw_db_url.startswith("postgresql://"):
    raw_db_url = raw_db_url.replace("postgresql://", "postgresql+psycopg://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = raw_db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}
db = SQLAlchemy(app)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# =============================================================================
# Models
# =============================================================================
class ProfitHistory(db.Model):
    __tablename__ = "profit_history"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False, default=0)
    cost = db.Column(db.Integer, nullable=False, default=0)
    ship = db.Column(db.Integer, nullable=False, default=0)
    fee = db.Column(db.Integer, nullable=False, default=0)
    profit = db.Column(db.Integer, nullable=False, default=0)
    margin = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    kind = db.Column(db.String(20), nullable=False, default="info")
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, default="")
    meta_json = db.Column(db.Text, default="{}")
    unread = db.Column(db.Boolean, nullable=False, default=True)
    snooze_until = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    @property
    def meta(self):
        try:
            return json.loads(self.meta_json or "{}")
        except Exception:
            return {}

class AppSettings(db.Model):
    __tablename__ = "app_settings"
    id = db.Column(db.Integer, primary_key=True)
    mail_enabled = db.Column(db.Boolean, nullable=False, default=False)
    mail_provider = db.Column(db.String(50), nullable=False, default="gmail")
    mail_from = db.Column(db.String(255), nullable=False, default="")
    mail_to = db.Column(db.String(1000), nullable=False, default="")
    mail_pass = db.Column(db.String(255), nullable=False, default="")
    profit_threshold = db.Column(db.Integer, nullable=False, default=5000)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    @staticmethod
    def get():
        s = AppSettings.query.get(1)
        if not s:
            s = AppSettings(
                id=1,
                mail_enabled=False,
                mail_provider="gmail",
                mail_from="",
                mail_to="",
                mail_pass="",
                profit_threshold=5000,
            )
            db.session.add(s)
            db.session.commit()
        return s

class OcrJob(db.Model):
    __tablename__ = "ocr_jobs"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    stored_path = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="uploaded")
    text = db.Column(db.Text, default="")
    error_msg = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# （中略：元のコード内容をそのまま維持）

@app.errorhandler(500)
def _500(e):
    print("[500]", traceback.format_exc())
    return render_template("errors/500.html"), 500

# ✅ 🔽🔽🔽 追加済みルート 🔽🔽🔽
@app.route("/search_setup")
def search_setup():
    return render_template("search_setup.html")
# ✅ 🔼🔼🔼 ここまで 🔼🔼🔼

# =============================================================================
# Main
# =============================================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
