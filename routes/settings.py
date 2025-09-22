from flask import Blueprint, render_template, request, redirect, url_for, flash

settings_bp = Blueprint("settings_bp", __name__)

# 設定画面
@settings_bp.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        # フォーム処理（例：通知設定保存）
        flash("設定を保存しました ✅")
        return redirect(url_for("settings_bp.settings"))
    # 仮データを渡す（本番はDBや設定ファイルから読み込む）
    s = {
        "mail_enabled": True,
        "mail_provider": "gmail",
        "mail_from": "example@gmail.com",
        "mail_to": "taro@example.com",
        "profit_threshold": 5000
    }
    return render_template("pages/settings.html", s=s)

# テストメール送信
@settings_bp.route("/settings/test", methods=["POST"])
def setting_test_mail():
    flash("テストメール送信しました ✉️")
    return redirect(url_for("settings_bp.settings"))

# 通知一覧
@settings_bp.route("/notifications")
def notifications():
    # 仮の通知データ（本番はDBやCSVから読み込む）
    rows = [
        {
            "id": 1,
            "title": "利益通知",
            "body": "1万円以上の利益が発生しました",
            "kind": "profit",
            "created_at": "2025-09-22 09:30",
            "unread": True,
            "meta": {"商品": "iPhone 14", "利益": "12,000円"}
        },
        {
            "id": 2,
            "title": "在庫アラート",
            "body": "在庫が少なくなっています",
            "kind": "warn",
            "created_at": "2025-09-21 15:10",
            "unread": False,
            "meta": {"商品": "AirPods Pro", "残り": "2個"}
        }
    ]
    return render_template("pages/notifications.html", rows=rows)
