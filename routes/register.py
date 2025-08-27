{% extends "base/layout.html" %}
{% block title %}新規登録{% endblock %}

{% block content %}
<h2>📝 新規登録フォーム</h2>
<form method="POST" class="form-grid">
  <label>ユーザー名</label>
  <input type="text" name="username" required>

  <label>ふりがな</label>
  <input type="text" name="kana" required>

  <label>生年月日</label>
  <input type="date" name="birthday" required>

  <label>年齢</label>
  <input type="number" name="age" min="0" required>

  <label>電話番号</label>
  <input type="tel" name="tel">

  <label>携帯番号</label>
  <input type="tel" name="mobile" required>

  <label>メールアドレス</label>
  <input type="email" name="email" required>

  <label>部署</label>
  <input type="text" name="department">

  <label>職種</label>
  <input type="text" name="role">

  <label>紹介者NO</label>
  <input type="text" name="intro_code">

  <label>ログインID</label>
  <input type="text" name="login_id" required>

  <label>パスワード</label>
  <input type="password" name="password" required>

  <button type="submit" class="btn btn-primary">登録する</button>
</form>
{% endblock %}
