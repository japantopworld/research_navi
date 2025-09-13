@app.route("/news", methods=["GET", "POST"])
def news():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    user_id = session.get("user_id")

    # タブ選択
    tab = request.args.get("tab", "inbox")

    messages = []
    if os.path.exists(SUPPORT_CSV):
        with open(SUPPORT_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            all_messages = list(reader)

        if tab == "inbox":
            messages = [m for m in all_messages if m["宛先"] == user_id]
        elif tab == "sent":
            messages = [m for m in all_messages if m["送信者"] == user_id]

    # 新規作成フォーム
    if request.method == "POST" and tab == "compose":
        to = request.form.get("to", "").strip()
        subject = request.form.get("subject", "").strip()
        body = request.form.get("body", "").strip()
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        new_msg = {
            "ID": str(len(messages)),
            "送信者": user_id,
            "宛先": to,
            "件名": subject,
            "本文": body,
            "添付": "",
            "ステータス": "未読",
            "送信日時": now
        }

        file_exists = os.path.exists(SUPPORT_CSV)
        with open(SUPPORT_CSV, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=new_msg.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(new_msg)

        return redirect(url_for("news", tab="sent"))

    return render_template("pages/news.html", tab=tab, messages=messages, user_id=user_id)


@app.route("/news/<int:msg_id>")
def news_detail(msg_id):
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    if not os.path.exists(SUPPORT_CSV):
        return "メッセージが存在しません", 404

    with open(SUPPORT_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        messages = list(reader)

    if msg_id < 0 or msg_id >= len(messages):
        return "メッセージが存在しません", 404

    message = messages[msg_id]

    # 既読に変更
    if message["ステータス"] == "未読" and message["宛先"] == session.get("user_id"):
        messages[msg_id]["ステータス"] = "既読"
        with open(SUPPORT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=messages[0].keys())
            writer.writeheader()
            writer.writerows(messages)

    return render_template("pages/news_detail.html", message=message, msg_id=msg_id)
