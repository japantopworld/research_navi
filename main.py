from flask import Flask, render_template, request, redirect, url_for, session
import csv
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

USERS_FILE = 'users.csv'

# 管理者情報（特別扱い）
ADMIN_ID = 'KING1192'
ADMIN_PASS = '11922960'

@app.route('/')
def home():
    if 'user_id' in session:
        if session['user_id'] == ADMIN_ID:
            return f'👑 管理者ログイン成功：{session["user_id"]}'
        else:
            return f'✅ 一般ユーザーとしてログイン中：{session["user_id"]}'
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        job_code = request.form['job_code'].upper()
        ref_code = request.form['ref_code'].upper()
        birthday = request.form['birthday']
        branch = request.form['branch'].upper()
        password = request.form['password']

        if len(password) < 8:
            return '❌ パスワードは8文字以上である必要があります。'

        # ログインID構築：職種 + 紹介者 + 誕生日 + 枝番号
        login_id = job_code + ref_code + birthday + branch

        # 保存処理
        with open(USERS_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([login_id, password])

        return f'✅ 登録完了！あなたのIDは「{login_id}」です。<br><a href="/login">ログインへ</a>'
    
    return render_template('pages/register_worker.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_id = request.form['login_id']
        password = request.form['password']

        # 管理者チェック
        if login_id == ADMIN_ID and password == ADMIN_PASS:
            session['user_id'] = login_id
            return redirect(url_for('home'))

        # 一般ユーザー認証
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row[0] == login_id and row[1] == password:
                        session['user_id'] = login_id
                        return redirect(url_for('home'))

        return '❌ IDまたはパスワードが間違っています。'
    
    return render_template('pages/login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
