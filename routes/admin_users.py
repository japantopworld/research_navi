# routes/admin_users.py
from flask import Blueprint, render_template, session, redirect, url_for
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

admin_users_bp = Blueprint("admin_users_bp", __name__)

SCOPES = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
CREDS_FILE = os.path.join("credentials", "service_account.json")
SPREADSHEET_KEY = "1XwTbWlJw9y6nsGxMwMiIko2wyEX88kMfez83hFTfz84"
SHEET_NAME = "users_register_data"

def get_worksheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPES)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SPREADSHEET_KEY)
    return spreadsheet.worksheet(SHEET_NAME)

@admin_users_bp.route("/admin/users")
def view_users():
    # ここでログインチェックもできる（仮に管理者専用）
    if session.get("user_id") != "KING1219":  # 管理者IDを固定
        return "権限がありません", 403

    worksheet = get_worksheet()
    users = worksheet.get_all_records()
    return render_template("admin/user_list.html", users=users)
