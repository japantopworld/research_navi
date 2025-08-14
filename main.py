{% extends "base/layout.html" %}
{% block title %}利益ランキング | リサーチナビ{% endblock %}
{% block content %}

<h1>利益ランキング <small style="color:#6b7280;font-size:.8em">（{{ label }}）</small></h1>

<!-- 期間フィルタ -->
<nav class="filter">
  <a class="btn {{ 'on' if days=='7' }}" href="{{ url_for('ranking', days='7') }}">7日</a>
  <a class="btn {{ 'on' if days=='30' }}" href="{{ url_for('ranking', days='30') }}">30日</a>
  <a class="btn {{ 'on' if days=='90' }}" href="{{ url_for('ranking', days='90') }}">90日</a>
  <a class="btn {{ 'on' if days=='365' }}" href="{{ url_for('ranking', days='365') }}">1年</a>
  <a class="btn {{ 'on' if days=='all' }}" href="{{ url_for('ranking', days='all') }}">全期間</a>
</nav>

{% if rows and rows|length %}
  <!-- 上位3件：カード -->
  <section class="top3">
    {% for r in rows[:3] %}
    <article class="top-card">
      <div class="rank-badge">#{{ loop.index }}</div>
      <div class="meta">
        <h3 class="name">{{ r.name }}</h3>
        <div class="sub">
          <span class="pf">PF: {{ r.platform }}</span>
          <span class="date">{{ r.created_at.strftime("%Y-%m-%d %H:%M") }}</span>
        </div>
      </div>
      <dl class="kpis">
        <div><dt>販売</dt><dd>{{ r.price|yen }}</dd></div>
        <div><dt>仕入</dt><dd>{{ r.cost|yen }}</dd></div>
        <div><dt>送料</dt><dd>{{ r.ship|yen }}</dd></div>
        <div><dt>手数料</dt><dd>{{ r.fee|yen }}</dd></div>
        <div class="profit"><dt>利益</dt><dd class="{{ 'pos' if r.profit>=0 else 'neg' }}">{{ r.profit|yen }}</dd></div>
        <div><dt>利益率</dt><dd>{{ r.margin }}%</dd></div>
      </dl>
    </article>
    {% endfor %}
  </section>

  <!-- 4位以降：テーブル -->
  {% if rows|length > 3 %}
  <section class="others">
    <div class="table-wrap">
      <table class="table">
        <thead>
          <tr>
            <th>#</th>
            <th>日時</th>
            <th>商品名</th>
            <th>PF</th>
            <th class="num">販売</th>
            <th class="num">仕入</th>
            <th class="num">送料</th>
            <th class="num">手数料</th>
            <th class="num">利益</th>
            <th class="num">利益率</th>
          </tr>
        </thead>
        <tbody>
          {% for r in rows[3:] %}
          <tr>
            <td>{{ loop.index + 3 }}</td>
            <td>{{ r.created_at.strftime("%Y-%m-%d %H:%M") }}</td>
            <td class="name">{{ r.name }}</td>
            <td>{{ r.platform }}</td>
            <td class="num">{{ r.price|yen }}</td>
            <td class="num">{{ r.cost|yen }}</td>
            <td class="num">{{ r.ship|yen }}</td>
            <td class="num">{{ r.fee|yen }}</td>
            <td class="num {{ 'pos' if r.profit>=0 else 'neg' }}">{{ r.profit|yen }}</td>
            <td class="num">{{ r.margin }}%</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </section>
  {% endif %}
{% else %}
  <p>ランキング対象のデータがありません。まずは <a href="{{ url_for('profit') }}">利益計算</a> でデータを保存してください。</p>
{% endif %}

<style>
.filter{display:flex;gap:8px;margin:10px 0 14px}
.filter .btn{
  padding:8px 10px;border:1px solid #e5e7eb;border-radius:10px;background:#fff;cursor:pointer;text-decoration:none;color:#111
}
.filter .btn.on{background:#111;color:#fff;border-color:#111}

.top3{display:grid;gap:14px;margin:12px 0}
@media (min-width:900px){.top3{grid-template-columns:repeat(3,minmax(0,1fr))}}
.top-card{
  position:relative;background:#fff;border:1px solid #e5e7eb;border-radius:14px;padding:14px;
  box-shadow:0 1px 8px rgba(2,6,23,.03);
}
.rank-badge{
  position:absolute;top:-10px;left:-10px;background:#111;color:#fff;padding:6px 10px;border-radius:12px;font-weight:700;
}
.top-card .name{margin:0 0 6px 0;font-size:16px;line-height:1.4}
.top-card .sub{color:#6b7280;font-size:12px;display:flex;gap:8px}
.kpis{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-top:10px}
.kpis dt{font-size:11px;color:#6b7280}
.kpis dd{margin:2px 0 0 0;font-weight:600}
.kpis .profit dd{font-size:18px}
.pos{color:#0a7f20}
.neg{color:#b91c1c}

.table-wrap{overflow:auto;border:1px solid #e5e7eb;border-radius:10px;margin-top:14px}
.table{width:100%;border-collapse:collapse;background:#fff}
.table th,.table td{padding:10px;border-bottom:1px solid #f1f5f9;white-space:nowrap}
.table thead th{position:sticky;top:0;background:#f8fafc;font-weight:700}
.table .num{text-align:right}
.table td.name{max-width:380px;overflow:hidden;text-overflow:ellipsis}
</style>

{% endblock %}
