# routes/auth.py

from flask import Blueprint, render_template, request, redirect, url_for, session

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/login")
def login():
    return render_template("auth/login.html")

@auth_bp.route("/register")
def register():
    return render_template("auth/register.html")
