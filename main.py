{% extends "base/layout.html" %}
{% block title %}マイページ | リサーチナビ{% endblock %}
{% block content %}

<!-- ▼ ナビバーを直書きで追加 ▼ -->
<nav class="topnav">
  <div class="nav-buttons">
    <a href="{{ url_for('index') }}" class="btn">🏠 ホーム</a>
    <a href="{{ url_for('support') }}" class="btn">💬 サポート</a>
    <a href="{{ url_for('services') }}" class="btn">📋 サービス一覧</a>
    <a href="{{ url_for('news') }}" class="btn">📰 お知らせ一覧</a>
    <a href="{{ url_for('mypage', user_id=session.get('user_id')) }}" class="btn">👤 マイページ</a>
    <a href="{{ url_for('settings') }}" class="btn">⚙️ 各種設定</a>
    <a href="{{ url_for('logout') }}" class="btn btn-ghost">↩︎ ログアウト</a>
  </div>
</nav>

<style>
  .topnav {
    position: sticky; top: 0; z-index: 100;
    background: #fff;
    border-bottom: 1px solid rgba(0,0,0,.08);
    padding: .8rem 1rem;
  }
  .nav-buttons {
    display: flex; flex-wrap: wrap; justify-content: center; gap: .8rem;
  }
  .btn {
    display: inline-block; padding: .6rem 1.1rem; border-radius: .6rem;
    text-decoration: none; font-weight: 700;
    background: #dc2626;
    color: #ffeb3b;
    transition: transform .08s ease, opacity .2s ease;
  }
  .btn:hover { transform: translateY(-2px); opacity: .9; }
  .btn-ghost {
    background: transparent;
    border: 1px solid #dc2626;
    color: #dc2626;
  }
  .btn-ghost:hover {
    background: #dc2626;
    color: #ffeb3b;
  }
</style>
<!-- ▲ ナビバーここまで ▲ -->

<div class="mypage-card" style="max-width:600px;margin:20vh auto;background:#fff;border-radius:1rem;box-shadow:0 6px 20px rgba(0,0,0,.1);padding:2rem;text-align:center;">
  <h1 style="font-size:2rem;color:#dc2626;margin-bottom:1.5rem;">
    ようこそ {{ display_name }} さん
  </h1>

  <a href="{{ url_for('logout') }}" class="btn-logout"
     style="display:inline-block;margin-top:2rem;padding:.8rem 1.5rem;
            background:#dc2626;color:#ffeb3b;border:none;border-radius:.6rem;
            font-weight:bold;cursor:pointer;text-decoration:none;">
    ↩︎ ログアウト
  </a>
</div>

{% endblock %}
