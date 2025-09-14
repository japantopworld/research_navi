@static_pages_bp.route("/contact", methods=["GET"])
def contact():
    return render_template("pages/contact.html")

@static_pages_bp.route("/send_contact", methods=["POST"])
def send_contact():
    # フォームデータ取得
    from flask import request, flash, redirect, url_for
    name = request.form.get("name")
    email = request.form.get("email")
    subject = request.form.get("subject")
    message = request.form.get("message")

    # TODO: メール送信処理を実装（SMTP or API）
    print(f"[CONTACT] {name} ({email}) 件名:{subject} 内容:{message}")

    flash("お問い合わせを受け付けました。担当者よりご連絡いたします。", "success")
    return redirect(url_for("static_pages.contact"))
