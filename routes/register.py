from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

register_bp = Blueprint("register_bp", __name__)

# Google Sheets 設定
SCOPES = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
CREDS_FILE = os.path.join("credentials", "service_account.json")
SPREADSHEET_KEY = "1XwTbWlJw9y6nsGxMwMiIko2wyEX88kMfez83hFTfz84"
SHEET_NAME = "users_register_data"  # ✅ シート名を変更

DEPARTMENTS = {
    "KIN": "鳳陽管理職(その他)",
    "BYR": "バイヤー",
    "KEI": "経理",
    "HAN": "販売員",
    "BUT": "物流",
    "GOT": "合統括"
}

def get_worksheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPES)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SPREADSHEET_KEY)
    return spreadsheet.worksheet(SHEET_NAME)

def generate_login_id(department_code, birthday_str, intro_code_alpha, existing_ids):
    try:
        birthday = datetime.strptime(birthday_str, "%Y/%m/%d")
        mmdd = birthday.strftime("%m%d")
    except:
        return None

    if intro_code_alpha not in ["A", "B", "C", "D", "E"]:
        return None

    base = f"{department_code}{intro_code_alpha}{mmdd}"
    suffix = intro_code_alpha
    similar = [row for row in existing_ids if row.startswith(f"{base}{suffix}")]
    serial = len(similar) + 1
    return f"{base}{suffix}{serial}"

@register_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        kana = request.form.get("kana")
        birthday = request.form.get("birthday")
        tel = request.form.get("tel")
        mobile = request.form.get("mobile")
        email = request.form.get("email")
        department = request.form.get("department")
        intro_code_alpha = request.form.get("intro_code")
        password = request.form.get("password")

        # 入力チェック
        errors = []
        if not username:
            errors.append("ユーザー名が未入力です。")
        if not kana:
            errors.append("ふりがなが未入力です。")
        if not birthday:
            errors.append("生年月日が未入力です。")
        if not (tel or mobile):
            errors.append("電話番号または携帯番号を入力してください。")
        if not email:
            errors.append("メールアドレスが未入力です。")
        if not password:
            errors.append("パスワードが未入力です。")

        if errors:
            for e in errors:
                flash(e, "danger")
            return redirect(url_for("register_bp.register"))

        try:
            worksheet = get_worksheet()
            existing_data = worksheet.get_all_records()
            existing_ids = [row["ID"] for row in existing_data if "ID" in row]

            department_code = next((code for code, name in DEPARTMENTS.items() if name == department), "KIN")
            login_id = generate_login_id(department_code, birthday, intro_code_alpha, existing_ids)

            age = datetime.today().year - datetime.strptime(birthday, "%Y/%m/%d").year

            new_row = [
                username,
                kana,
                birthday,
                age,
                tel,
                mobile,
                email,
                department,
                intro_code_alpha,
                login_id,
                password
            ]

            worksheet.append_row(new_row)
            flash(f"登録が完了しました。あなたのログインIDは {login_id} です。", "success")
            return redirect(url_for("login_bp.login"))

        except Exception as e:
            flash(f"登録中にエラーが発生しました: {str(e)}", "danger")
            return redirect(url_for("register_bp.register"))

    return render_template("auth/register.html", departments=DEPARTMENTS.values(), intro_codes=["A", "B", "C", "D", "E"])
