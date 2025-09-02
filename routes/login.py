from flask import Blueprint, render_template, request, redirect, url_for, session
import csv
import os

login_bp = Blueprint("login_bp", __name__)

@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # 認証処理（省略）
        return redirect(url_for("mypage_bp.mypage"))
    return render_template("auth/login.html")

@login_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_bp.login"))
