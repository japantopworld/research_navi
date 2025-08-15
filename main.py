# main.py
from __future__ import annotations
import os
from datetime import datetime
from typing import Dict, Any, Optional

from flask import (
    Flask, render_template, request, redirect, url_for, flash
)

# ---- DB（SQLAlchemy Core） -----------------------------
from sqlalchemy import (
    create_engine, text
)
from sqlalchemy.engine import Engine

# ---- メール --------------------------------------------
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# ========================================================
# Flask
# ========================================================
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "research-navi-dev")

# ========================================================
# DB 接続（Render の Postgres を優先。なければローカル SQLite）
# ========================================================
def _build_engine() -> Engine:
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        # Render の DSN は postgresql:// 形式なので psycopg 用に変換
        if db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
    else:
        os.makedirs("data", exist_ok=True)
        db_url = "sqlite:///data/research_navi.db"
    return create_engine(db_url, future=True)

engine: Engine = _build_engine()

# 初期化（設定テーブルと 1 レコードを用意）
def init_db() -> None:
    with engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS app_settings (
            id               INTEGER PRIMARY KEY,
            mail_enabled     INTEGER NOT NULL DEFAULT 0,
            mail_provider    TEXT    NOT NULL DEFAULT 'gmail',
            mail_from        TEXT    NOT NULL DEFAULT '',
            mail_to          TEXT    NOT NULL DEFAULT '',
            mail_pass        TEXT    NOT NULL DEFAULT '',
            profit_threshold INTEGER NOT NULL DEFAULT 5000,
            updated_at       TEXT    NOT NULL
        );
        """))
        # SQLite は AUTOINCREMENT、Postgres は SERIAL の代わりに上記 PK でOK
        row = conn.execute(text("SELECT id FROM app_settings WHERE id = 1")).fetchone()
        if not row:
            conn.execute(text("""
                INSERT INTO app_settings
                (id, mail_enabled, mail_provider, mail_from, mail_to, mail_pass, profit_threshold, updated_at)
                VALUES (1, 0, 'gmail', '', '', '', 5000, :now)
            """), {"now": datetime.utcnow().isoformat()})

init_db()

# ========================================================
# 設定の読み書き
# ========================================================
def get_settings() -> Dict[str, Any]:
    with engine.begin() as conn:
        row = conn.execute(text("SELECT * FROM app_settings WHERE id = 1")).mappings().first()
        return dict(row)

def save_settings(data: Dict[str, Any], keep_password_if_blank: bool = True) -> None:
    # パスワードの空保存は「保持」にする
    if keep_password_if_blank:
        if not data.get("mail_pass"):
            current = get_settings()
            data["mail_pass"] = current.get("mail_pass", "")

    data["updated_at"] = datetime.utcnow().isoformat()
    with engine.begin() as conn:
        conn.execute(text("""
            UPDATE app_settings SET
              mail_enabled     = :mail_enabled,
              mail_provider    = :mail_provider,
              mail_from        = :mail_from,
              mail_to          = :mail_to,
              mail_pass        = :mail_pass,
              profit_threshold = :profit_threshold,
              updated_at       = :updated_at
            WHERE id = 1
        """), {
            "mail_enabled":     1 if str(data.get("mail_enabled", "0")) in ("1", "true", "on") else 0,
            "mail_provider":    data.get("mail_provider", "gmail"),
            "mail_from":        data.get("mail_from", "").strip(),
            "mail_to":          data.get("mail_to", "").strip(),
            "mail_pass":        data.get("mail_pass", ""),
            "profit_threshold": int(data.get("profit_threshold") or 0),
            "updated_at":       data["updated_at"],
        })

# ========================================================
# メール送信（Gmail アプリパスワード対応）
# ========================================================
def send_mail(subject: str, body: str, settings: Optional[Dict[str, Any]] = None) -> bool:
    s = settings or get_settings()

    if not s.get("mail_enabled"):
        return False  # 無効化時は送らない

    provider = (s.get("mail_provider") or "gmail").lower()
    mail_from = s.get("mail_from", "")
    mail_to   = s.get("mail_to", "")
    mail_pass = s.get("mail_pass", "")

    if provider != "gmail":
        # 将来拡張用（今は Gmail のみ）
        raise RuntimeError("現在は Gmail のみ対応です。")

    if not (mail_from and mail_to and mail_pass):
        raise RuntimeError("メール設定（送信元 / 宛先 / アプリパスワード）が不足しています。")

    msg = MIMEText(body, _charset="utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"]    = mail_from
    msg["To"]      = mail_to

    with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(mail_from, mail_pass)
        smtp.sendmail(mail_from, [a.strip() for a in mail_to.split(",") if a.strip()], msg.as_string())

    return True

# ========================================================
# Jinja フィルタ
# ========================================================
@app.template_filter("yen")
def yen(v) -> str:
    try:
        n = int(float(v))
    except Exception:
        return str(v)
    return f"¥{n:,}"

# ========================================================
# ルーティング（主要ページ）
# ========================================================
@app.route("/")
def home():
    return render_template("pages/home.html")

@app.route("/search")
def search():
    return render_template("pages/search.html")

@app.route("/profit")
def profit():
    return render_template("pages/profit.html")

@app.route("/history")
def history():
    return render_template("pages/history.html")

@app.route("/ranking")
def ranking():
    return render_template("pages/ranking.html")

@app.route("/notifications")
def notifications():
    return render_template("pages/notifications.html")

@app.route("/ocr")
def ocr():
    return render_template("pages/ocr.html")

@app.route("/suppliers")
def suppliers():
    return render_template("pages/suppliers.html")

# ========================================================
# 設定（GUI） + テスト送信
# ========================================================
@app.route("/setting", methods=["GET", "POST"])
def setting():
    if request.method == "POST":
        form = {
            "mail_enabled":     request.form.get("mail_enabled"),
            "mail_provider":    request.form.get("mail_provider", "gmail"),
            "mail_from":        request.form.get("mail_from", ""),
            "mail_to":          request.form.get("mail_to", ""),
            "mail_pass":        request.form.get("mail_pass", ""),   # 空なら保持
            "profit_threshold": request.form.get("profit_threshold", "5000"),
        }
        save_settings(form, keep_password_if_blank=True)
        flash("設定を保存しました。")
        return redirect(url_for("setting"))

    s = get_settings()
    return render_template("pages/setting.html", s=s)

@app.post("/setting/test-mail")
def setting_test_mail():
    s = get_settings()
    try:
        ok = send_mail(
            subject="【リサーチナビ】テスト送信",
            body=(
                "これはテストメールです。\n\n"
                f"送信元: {s.get('mail_from')}\n"
                f"送信先: {s.get('mail_to')}\n"
                f"閾値  : {s.get('profit_threshold')} 円\n"
                f"時刻  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            ),
            settings=s
        )
        if ok:
            flash("テストメールを送信しました。Gmail の受信トレイをご確認ください。")
        else:
            flash("通知は無効です（チェックを入れて保存してください）。")
    except Exception as e:
        flash(f"テスト送信に失敗しました：{e}")
    return redirect(url_for("setting"))

# ========================================================
# エラーハンドラ
# ========================================================
@app.errorhandler(404)
def not_found(e):
    return render_template("errors/404.html"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("errors/500.html"), 500

# ========================================================
if __name__ == "__main__":
    # ローカル開発用
    app.run(debug=True, host="0.0.0.0", port=5000)
