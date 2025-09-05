# routes/admin.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
import csv
import os
from datetime import datetime

admin_bp = Blueprint("admin_bp", __name__)

NOTIFICATION_FILE = "data/notifications.csv"

# 通知一覧表示
@admin_bp.route("/admin")
def admin_dashboard():
    notifications = []
    if os.path.exists(NOTIFICATION_FILE):
        with open(NOTIFICATION_FILE, newline='', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                notifications.append(row)
    notifications.sort(key=lambda x: x["timestamp"], reverse=True)
    return render_template("admin/admin.html", notifications=notifications)

# 通知追加
@admin_bp.route("/admin/add_notification", methods=["POST"])
def add_notification():
    title = request.form.get("title")
    content = request.form.get("content")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ファイルがなければ作成＆ヘッダー
    file_exists = os.path.exists(NOTIFICATION_FILE)
    with open(NOTIFICATION_FILE, mode="a", newline='', encoding="utf-8") as csvfile:
        fieldnames = ["id", "title", "content", "timestamp"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        new_id = int(datetime.now().timestamp())  # 一意なID
        writer.writerow({
            "id": new_id,
            "title": title,
            "content": content,
            "timestamp": timestamp
        })

    flash("通知を追加しました", "success")
    return redirect(url_for("admin_bp.admin_dashboard"))

# 通知削除
@admin_bp.route("/admin/delete_notification/<int:note_id>", methods=["POST"])
def delete_notification(note_id):
    rows = []
    deleted = False
    if os.path.exists(NOTIFICATION_FILE):
        with open(NOTIFICATION_FILE, newline='', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if int(row["id"]) != note_id:
                    rows.append(row)
                else:
                    deleted = True

        with open(NOTIFICATION_FILE, mode="w", newline='', encoding="utf-8") as csvfile:
            fieldnames = ["id", "title", "content", "timestamp"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    if deleted:
        flash("通知を削除しました", "info")
    else:
        flash("通知が見つかりませんでした", "warning")

    return redirect(url_for("admin_bp.admin_dashboard"))
