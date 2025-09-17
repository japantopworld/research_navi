リサーチナビ - 総合部門（全体管理・人事・サポート）モジュール

■ 追加ファイル
- routes/general.py （Blueprint: general_bp /admin 配下）
- models/general.py （SQLAlchemy モデル）
- utils/auth.py （ログイン・ロール制御ユーティリティ）
- templates/admin/*.html （管理画面テンプレート）
- static/css/admin.css / static/js/admin.js

■ 統合手順（抜粋）
1) app 初期化で DB と Blueprint を登録：
   from models.general import db
   from routes.general import general_bp
   app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///research_navi.db'
   db.init_app(app)
   app.register_blueprint(general_bp)
   app.config['FEATURE_ADMIN'] = True  # 管理画面を有効化

2) ベースレイアウト base/layout.html に admin.css を読み込み：
   <link rel="stylesheet" href="{{ url_for('static', filename='css/admin.css') }}">

3) DB 初期化（flask shell などで）
   from models.general import db, Department, Role
   db.create_all()
   # 初期部署/ロール
   if not Department.query.filter_by(code='GEN').first():
       db.session.add(Department(code='GEN', name='総合'))
   for r in ('admin','staff','contractor'):
       from models.general import Role
       if not Role.query.filter_by(name=r).first():
           db.session.add(Role(name=r))
   db.session.commit()

4) セッション例：ログイン処理で
   session['user'] = {'user_id':'KING1219','role':'admin','department':'GEN','display_name':'管理者'}

5) ナビバーに管理リンクを追加：
   <a href="{{ url_for('general_bp.dashboard') }}">総合（管理）</a>

6) 既存のログイン Blueprint が login_bp.login を持つ前提です。
   無い場合は utils/auth.py のリダイレクト先を修正してください。

以上。
