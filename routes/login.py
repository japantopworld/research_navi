from flask import Blueprint, render_template, request, redirect, session, url_for

login_bp = Blueprint("login", __name__)

# ダミーユーザー（本番はDB管理）
DUMMY_USERS = {
    "admin": "password123",import csv
from flask import Blueprint, render_template, request, redirect, session

login_bp = Blueprint('login_bp', __name__)

def load_usernames_from_csv():
    with open('data/workers.csv', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return [row['id'] for row in reader]  # 「id」列からIDだけ取り出す

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    usernames = load_usernames_from_csv()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # 認証ロジックをここに追加（省略）

        session['user'] = username
        return redirect('/')
    
    return render_template('pages/login.html', usernames=usernames)

    "user": "testpass"
}

@login_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in DUMMY_USERS and DUMMY_USERS[username] == password:
            session["user"] = username
            return redirect(url_for("home"))
        else:
            error = "ログイン失敗：ユーザー名またはパスワードが違います"
    return render_template("pages/login.html", error=error)

@login_bp.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login.login"))
