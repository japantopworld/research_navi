# リサーチナビ ダッシュボード（Flask）

## 1) ローカル起動
```bash
pip install -r requirements.txt
python main.py
# http://127.0.0.1:5000/ を開く
```

## 2) Render 等にデプロイ
- `render.yaml` と `Procfile` を含めています。
- Health Check は `/healthz`。

## 構成
```
.
├── main.py
├── requirements.txt
├── Procfile
├── render.yaml
├── data/
│   ├── transactions.csv
│   ├── stock.csv
│   └── alerts.csv
├── static/
│   └── css/styles.css
└── templates/
    ├── base/layout.html
    └── pages/
        ├── home.html
        └── dashboard.html
```

## 追記
- CSVは日本時間（JST）ベースで本日・今月集計。
- 直近7日の売上推移をChart.jsで描画。
- 壊れたCSVでもアプリが落ちないように `safe_read_csv` を実装。
