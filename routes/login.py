from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

login_bp = Blueprint("login_bp", __name__)

# Google Sheets 認証情報
SCOPES = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
CREDS_FILE = os.path.join("credentials", "service_account.json")
SPREADSHEET_KEY = "1XwTbWlJw9y6nsGxMwMiIko2wyEX88kMfez83hFTfz84"
SHEET_NAME = "users_register_data"

def get_worksheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPES)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SPREADSHEET_KEY)
    return spreadsheet.worksheet(SHEET_NAME)

@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_id = request.form["login_id"]
        password = request.form["password"]

        try:
            worksheet = get_worksheet()
            records = worksheet.get_all_records()

            for row in records:
                if row["ID"] == login_id and str(row["PASS"]) == password:
                    # セッションに基本データ
                    session["user_id"] = login_id
                    session["user_name"] = row["ユーザー名"]

                    # ✅ マイページ用に情報保存
                    session["user_info"] = {
                        "username": row["ユーザー名"],
                        "kana": row["ふりがな"],
                        "birthday": row["生年月日"],
                        "age": row["年齢"],
                        "tel": row["電話番号"],
                        "mobile": row["携帯番号"],
                        "email": row["メールアドレス"],
                        "department": row["部署"],
                        "intro_code": row["紹介者NO"],
                        "login_id": row["ID"]
                    }

                    flash("ログインに成功しました！", "success")
                    return redirect(url_for("home_bp.mypage"))  # ✅ 修正済み

            flash("ログインIDまたはパスワードが違います", "danger")
            return redirect(url_for("login_bp.login"))

        except Exception as e:
            flash(f"エラーが発生しました: {str(e)}", "danger")
            return redirect(url_for("login_bp.login"))

    return render_template("auth/login.html")
