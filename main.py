# main.py
import os
from flask import Flask, render_template, redirect, url_for, Response

def create_app():
    app = Flask(
        __name__,
        template_folder="templates",  # 例: templates/pages/home.html
        static_folder="static"        # 例: static/img/mascot.jpeg
    )
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    # -----------------------------
    # Health check (Render 用)
    # -----------------------------
    @app.route("/healthz")
    def healthz():
        return Response("ok", status=200, mimetype="text/plain")

    # -----------------------------
    # Blueprint 登録
    # -----------------------------
    # ✅ auth_bp を /login, /logout, /register で使う前提
    try:
        from routes.auth import auth_bp
        # url_prefix は付けない（/auth を付けると /auth/register になってズレる）
        app.register_blueprint(auth_bp)
        print("[OK] Registered: routes.auth.auth_bp")
    except Exception as e:
        print(f"[WARN] auth_bp not registered: {e}")

    # 他のBPがあればここで同様に登録（無ければスルーしてOK）
    # try:
    #     from routes.home import home_bp
    #     app.register_blueprint(home_bp)
    # except Exception as e:
    #     print(f"[WARN] home_bp not registered: {e}")

    # -----------------------------
    # トップページ
    # -----------------------------
    @app.route("/")
    def index():
        # 1) pages/home.html があればそれを出す
        try:
            return render_template("pages/home.html")
        except Exception:
            # 2) ない場合でもとにかく使える暫定トップを返す
            html = f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><title>Research Navi</title>
<meta name="viewport" content="width=device-width, initial-scale=1"></head>
<body style="font-family:system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,'Noto Sans JP','Hiragino Kaku Gothic ProN','ヒラギノ角ゴ ProN W3','Yu Gothic UI','YuGothic','Meiryo',sans-serif; padding:24px">
  <h1 style="margin-bottom:8px;">リサーチナビ</h1>
  <p style="color:#6b7280;margin-top:0;">最強のせどり＆物販支援ツール</p>
  <div style="display:flex;gap:12px;margin-top:20px;">
    <a href="{url_for('auth_bp.login')}" style="padding:10px 16px;background:#1e3a8a;color:#fff;text-decoration:none;border-radius:8px;">ログイン</a>
    <a href="{url_for('auth_bp.register')}" style="padding:10px 16px;background:#6b7280;color:#fff;text-decoration:none;border-radius:8px;">新規登録</a>
  </div>
</body></html>"""
            return Response(html, status=200, mimetype="text/html")

    # -----------------------------
    # エラーハンドラ
    # -----------------------------
    @app.errorhandler(404)
    def not_found(e):
        try:
            return render_template("errors/404.html"), 404
        except Exception:
            return Response("404 Not Found", status=404)

    @app.errorhandler(500)
    def server_error(e):
        try:
            return render_template("errors/500.html", error=e), 500
        except Exception:
            return Response("500 Internal Server Error", status=500)

    # -----------------------------
    # ルート一覧ダンプ（任意）
    # 環境変数 DUMP_ROUTES=1 のとき /__routes を有効化
    # -----------------------------
    if os.getenv("DUMP_ROUTES", "0") == "1":
        @app.route("/__routes")
        def __routes():
            lines = [str(r) for r in app.url_map.iter_rules()]
            return Response("\n".join(lines), mimetype="text/plain")

        with app.app_context():
            print("=== URL MAP ===")
            for r in app.url_map.iter_rules():
                print(r)

    return app


app = create_app()

if __name__ == "__main__":
    # ローカル実行用（Render では Proc/コマンドで waitress を使う想定でもOK）
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
