from flask import Blueprint, render_template, request, redirect, url_for, session
import csv
import os

login_bp = Blueprint("login_bp", __name__)

USER_CSV_PATH = "data/users.csv"
ADMIN_ID = "KING1192"
ADMIN_PASS = "11922960"

@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_id = request.form["login_id"]
        password = request.form["password"]

        if login_id == ADMIN_ID and password == ADMIN_PASS:
            session["user_id"] = login_id
            session["role"] = "parent"
            return redirect(url_for("login_bp.parent_mypage"))

        if not os.path.exists(USER_CSV_PATH):
            return "ユーザーデータが見つかりません", 500

        with open(USER_CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["ID"] == login_id and row["PASS"] == password:
                    session["user_id"] = login_id
                    session["role"] = "child"
                    return redirect(url_for("login_bp.child_mypage"))

        return "ログイン失敗"

    return render_template("pages/login.html")

@login_bp.route("/parent/mypage")
def parent_mypage():
    if session.get("role") != "parent":
        return redirect(url_for("login_bp.login"))
    return render_template("pages/parent_mypage.html")

@login_bp.route("/child/mypage")
def child_mypage():
    if session.get("role") != "child":
        return redirect(url_for("login_bp.login"))
    return render_template("pages/child_mypage.html")
