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
    return render_template("pages/notifications.html")
